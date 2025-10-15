from django.utils import timezone
from .models import Product, Loss, Category
from datetime import timedelta

def process_expired_products():
    today = timezone.now().date()
    expired_products = Product.objects.filter(dlc__lt=today, is_active=True)

    default_category, _ = Category.objects.get_or_create(name="Périmé")
    
    for product in expired_products:
        # Ajouter à la liste des pertes
        Loss.objects.create(
            product=product,
            category=default_category,
            reason="DLC dépassée",
            quantity=1,  # Quantité par défaut, ajuster si nécessaire
            price=0.0,   # Prix par défaut, ajuster si nécessaire
            loss_date=today
        )
        # Désactiver le produit
        product.is_active = False
        product.save()