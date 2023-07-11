from typing import Any, List, Optional, Tuple
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from . import models
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.core.validators import MinValueValidator


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "total_products"]
    search_fields = ["title"]  # For autocomplete fields in ProductAdmin

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
    prepopulated_fields = {"slug": ["title"]}
    search_fields = ["title"]

    # The collection drop down list could be very long hence we need to add search in collection field
    # so we do not need to create huge drop down list and rather we will search fields by 'title' of collection
    # in the drop down.
    # Hence we need to add 'collection' as autocomplete_fields and to do that we need to add 'title' in
    # as search_fields in CollectionAdmin class.

    # We need to add 'title' as search_fields in CollectionAdmin class (searching collection in dropdown list by title)
    # because Django does not know how to search 'collection' field.
    # same is applied to search_fields = ["title"] because product attributes is being used by Order classAdmin
    # by autocomplete_fields.
    autocomplete_fields = ["collection"]
    actions = ["clear_inventory"]
    list_display = [
        "title",
        "slug",
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

        self.message_user(
            request,
            f"{updated_count} product(s) were successfully updated.",
            messages.ERROR,
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders_count"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]
    list_editable = ["membership"]
    list_per_page = 10
    list_select_related = ["user"] # To avoid sending separate query for user as used in ordering below
    ordering = ["user__first_name", "user__last_name"]

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


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    model = models.OrderItem
    # By default we will see 3 rows for inline items.
    # If we do not want to see these 3 rows then we set extra to '0'.
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["placed_at", "payment_status", "customer"]
    inlines = [OrderItemInline]
    autocomplete_fields = ["customer"]
    list_per_page = 5
    list_editable = ["payment_status"]
