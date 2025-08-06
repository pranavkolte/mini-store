from rest_framework import serializers

from products.models.product_models import Products


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'
        read_only_fields = ('product_id', 'created_by', 'created_at', 'updated_at')
