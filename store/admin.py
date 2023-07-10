from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from . import models
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "total_products"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(total_products=Count("products"))

    @admin.display(ordering="total_products")
    def total_products(self, collection: models.Collection):
        # reverse('admin:app_model_page')
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html('<a href="{}">{}</a>', url, collection.total_products)
        # return collection.total_products


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [("<10", "Low")]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ["clear_inventory"]
    list_display = [
        "title",
        "unit_price",
        "inventory",
        "inventory_status",
        "collection_title",
    ]
    list_editable = ["unit_price"]
    list_per_page = 15
    list_select_related = ["collection"]
    list_filter = ["collection", "last_update", InventoryFilter]

    @admin.display(ordering="inventory")
    def inventory_status(self, product: models.Product):
        if product.inventory < 80:
            return "Low"
        return "Ok"

    def collection_title(self, product: models.Product):
        return product.collection.title

    @admin.action(description="Clear Inventory")
    def clear_inventory(self, request: HttpRequest, queryset: QuerySet[Any]):
        updated_count = queryset.update(inventory=0)

        self.message_user = (
            request,
            f"{updated_count} products were successfully updated."
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders_count"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(total_orders=Count("orders"))

    @admin.display(ordering="orders_count")
    def orders_count(self, customer: models.Customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html('<a href="{}">{}</a>', url, customer.total_orders)


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["placed_at", "payment_status", "customer"]
    list_per_page = 5
    list_editable = ["payment_status"]