from rest_framework import serializers
from .models import Product, Loss, Category

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'type', 'dlc', 'is_active']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class LossSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', required=False, allow_null=True
    )
    product_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', required=False, allow_null=True
    )

    class Meta:
        model = Loss
        fields = ['id', 'product', 'product_id', 'product_name', 'category', 'category_id', 'reason', 'loss_date', 'quantity', 'price']

    def validate(self, data):
        product = data.get('product')
        product_name = data.get('product_name', '')
        if not product and not product_name:
            raise serializers.ValidationError("Vous devez spécifier un produit ou un nom de produit.")
        return data

    def create(self, validated_data):
        product = validated_data.get('product')
        product_name = validated_data.get('product_name', '')
        if not product and product_name:
            validated_data['product'] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        product = validated_data.get('product')
        product_name = validated_data.get('product_name', '')
        if not product and product_name:
            validated_data['product'] = None
        return super().update(instance, validated_data)