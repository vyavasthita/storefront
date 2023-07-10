from decimal import Decimal
from rest_framework import serializers
from . import models


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ["id", "title", "products_count"]

    products_count = serializers.IntegerField()

    def get_product_count(self, collection):
        return collection.products.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ["id", "title", "unit_price", "price_with_tax", "collection"]

    price_with_tax = serializers.SerializerMethodField(method_name="get_price_with_tax")

    collection = serializers.HyperlinkedRelatedField(
        queryset=models.Collection.objects.all(), view_name="collection-detail"
    )

    def get_price_with_tax(self, product):
        return product.unit_price * Decimal(1.18)

    def create(self, validated_data):
        product = models.Product(**validated_data)
        product.save()
        return product

    def update(self, instance: models.Product, validated_data):
        instance.unit_price = validated_data.get("unit_price")
        instance.save()
        return instance


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ["id", "name", "description", "date"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return models.Review.objects.create(product_id=product_id, **validated_data)


class CartItemForCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ["product", "quantity", "total_price"]

    product = ProductSerializer()

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: models.CartItem):
        return cart_item.product.unit_price * cart_item.quantity


class CreateCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ["id"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ["id", "created_at", "cartitems", "total_cart_value"]
        read_only_fields = ["id", "created_at", "cartitems", "total_cart_value"]

    cartitems = CartItemForCartSerializer(many=True, read_only=True)

    total_cart_value = serializers.SerializerMethodField()

    def get_total_cart_value(self, cart: models.Cart):
        total_value = 0

        for cart_item in cart.cartitems.all():
            total_value += cart_item.product.unit_price * cart_item.quantity

        return total_value


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ["product", "quantity"]

    def create(self, validated_data):
        return models.CartItem.objects.create(
            cart_id=self.context["cart_id"], **validated_data
        )

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            cart_item = models.CartItem.objects.get(
                cart_id=cart_id, product_id=product_id
            )
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except models.CartItem.DoesNotExist:
            self.instance = models.CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance


class CartItemReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ["id", "product", "quantity"]

        product = serializers.StringRelatedField()


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ["quantity"]
