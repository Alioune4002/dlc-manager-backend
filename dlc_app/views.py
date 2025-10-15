from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, Loss, Category
from .serializers import ProductSerializer, LossSerializer, CategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from io import BytesIO
from xhtml2pdf import pisa
from django.http import FileResponse, JsonResponse

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class LossViewSet(viewsets.ModelViewSet):
    queryset = Loss.objects.all()
    serializer_class = LossSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@api_view(['GET'])
def losses_by_product(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    losses = Loss.objects.filter(
        loss_date__year=current_year,
        loss_date__month=current_month
    ).values('product__name', 'product_name').annotate(
        total_losses=Count('id'),
        total_cost=Sum('price')
    )
    result = []
    for loss in losses:
        product_name = loss['product__name'] or loss['product_name'] or 'Produit inconnu'
        total_cost = float(loss['total_cost'] or 0)
        result.append({
            'product_name': product_name,
            'total_losses': loss['total_losses'],
            'total_cost': total_cost
        })
    return Response(result)

@api_view(['GET'])
def losses_by_month(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    if not year or not month:
        return Response({"error": "Year and month are required"}, status=400)
    try:
        year = int(year)
        month = int(month)
        losses = Loss.objects.filter(loss_date__year=year, loss_date__month=month)
        serializer = LossSerializer(losses, many=True)
        return Response(serializer.data)
    except ValueError:
        return Response({"error": "Year and month must be integers"}, status=400)

@api_view(['GET'])
def download_losses_pdf(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    if not year or not month:
        return JsonResponse({"error": "Year and month are required"}, status=400)
    try:
        year = int(year)
        month = int(month)
        losses = Loss.objects.filter(loss_date__year=year, loss_date__month=month)
        print(f"Filtrage pour {year}-{month}: {losses.count()} pertes trouvées")  # Débogage
    except ValueError:
        return JsonResponse({"error": "Year and month must be integers"}, status=400)

    # Formatting month name
    month_names = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    month_name = month_names[month - 1]

    # Generate HTML content
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            @page {{ size: landscape; }}
        </style>
    </head>
    <body>
        <h1 style="text-align: center;">Rapport des Pertes - {month_name} {year}</h1>
        <table>
            <thead>
                <tr>
                    <th>Produit</th>
                    <th>Catégorie</th>
                    <th>Raison</th>
                    <th>Date</th>
                    <th>Quantité</th>
                    <th>Prix (€)</th>
                </tr>
            </thead>
            <tbody>
    """
    for loss in losses:
        product_name = (loss.product.name if loss.product else loss.product_name) or "Produit inconnu"
        category_name = loss.category.name if loss.category else "Aucune"
        reason = loss.reason or "Aucune"
        loss_date = str(loss.loss_date)
        quantity = str(loss.quantity)
        price = f"{float(loss.price):.2f}" if loss.price is not None else "0.00"
        html_content += f"""
            <tr>
                <td>{product_name}</td>
                <td>{category_name}</td>
                <td>{reason}</td>
                <td>{loss_date}</td>
                <td>{quantity}</td>
                <td>{price}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Convert HTML to PDF
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=buffer)
    if pisa_status.err:
        return JsonResponse({"error": "Erreur lors de la génération du PDF"}, status=500)

    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"Pertes_{year}_{month}.pdf",
        content_type='application/pdf'
    )

@api_view(['GET'])
def reminders(request):
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Produits à réduire (-30%) : veille de la DLC
    reduce_products = Product.objects.filter(dlc=tomorrow, is_active=True)
    reduce_list = [{"name": p.name, "dlc": p.dlc, "action": "Réduire à -30%"} for p in reduce_products]

    # Produits à retirer : DLC aujourd'hui
    withdraw_products = Product.objects.filter(dlc=today, is_active=True)
    withdraw_list = [{"name": p.name, "dlc": p.dlc, "action": "Retirer ce soir"} for p in withdraw_products]

    # Produits expirés : passer dans pertes
    expired_products = Product.objects.filter(dlc__lt=today, is_active=True)
    for product in expired_products:
        Loss.objects.create(
            product=product,
            product_name=product.name,
            category=None,
            reason="DLC dépassée",
            loss_date=today,
            quantity=1,
            price=None
        )
        product.is_active = False
        product.save()

    return Response({
        "reduce_tomorrow": reduce_list,
        "withdraw_today": withdraw_list
    })