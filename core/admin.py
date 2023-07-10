from django.contrib import admin
from store.admin import ProductAdmin
from tags.models import TaggedItem
from django.contrib.contenttypes.admin import GenericTabularInline
from store.models import Product

admin.site.unregister(Product)


class TagInline(GenericTabularInline):
    autocomplete_fields = ["tag"]
    model = TaggedItem
    extra = 0


@admin.register(Product)
class CustomeProductAdmin(ProductAdmin):
    inlines = [TagInline]


# Now we have new product admin so we need to unregister old Product

# admin.site.register(Product, CustomeProductAdmin)

# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import User


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": (
#                     "username",
#                     "password1",
#                     "password2",
#                     "email",
#                     "first_name",
#                     "last_name",
#                 ),
#             },
#         ),
#     )
