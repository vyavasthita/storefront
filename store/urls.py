from django.urls import path
from .views import (
    ProductViewSet,
    CollectionViewSet,
    ReviewViewSet,
    CartViewSet,
    CartItemViewSet,
    CustomerViewSet,
)
from rest_framework_nested.routers import (
    NestedSimpleRouter,
    SimpleRouter,
    DefaultRouter,
)

router = DefaultRouter()
router.register("product", ProductViewSet, basename="product")
router.register("collection", CollectionViewSet)
router.register("cart", CartViewSet)
router.register("customer", CustomerViewSet, basename="customer")

product_router = NestedSimpleRouter(router, "product", lookup="product")
product_router.register("review", ReviewViewSet, basename="product-reviews")

cart_router = NestedSimpleRouter(router, "cart", lookup="cart")
cart_router.register("cartitems", CartItemViewSet, basename="cart-cartitems")

urlpatterns = router.urls + product_router.urls + cart_router.urls
