from django.shortcuts import render
from django.http import HttpRequest
from .models import (
    Product,
    Order,
    OrderItem,
    Customer,
    Promotion,
    Collection,
    Review,
    Cart,
    CartItem,
)
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Sum
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    ProductSerializer,
    CollectionSerializer,
    ReviewSerializer,
    CreateCartSerializer,
    CartSerializer,
    CartItemCreateSerializer,
    CartItemReadSerializer,
    CartItemUpdateSerializer,
)
from rest_framework.pagination import PageNumberPagination
from .filters import ProductFilter
from .pagination import DefaultPagination


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ["collection_id"]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ["title"]
    ordering_fields = ["unit_price"]

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "Product can not be deleted, because it is associated with one or more order items."
                },
                status=405,
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products"))
    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCartSerializer
        else:
            return CartSerializer
    
    queryset = Cart.objects.prefetch_related("cartitems__product").all()


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "product"
        )

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartItemCreateSerializer
        elif self.request.method == "PATCH":
            return CartItemUpdateSerializer
        else:
            return CartItemReadSerializer
