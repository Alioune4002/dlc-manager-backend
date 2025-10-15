from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    dlc = models.DateField(null=True, blank=True)  # Déjà correct, mais on confirme
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.type.lower() == 'périssable':
            self.dlc = None  # Pas de DLC pour les produits périssables
        super().save(*args, **kwargs)

class Loss(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=100, blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    loss_date = models.DateField()
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Loss {self.id} - {self.product_name or self.product or 'No product'}"