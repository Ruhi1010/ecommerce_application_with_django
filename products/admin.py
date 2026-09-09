from django.contrib import admin

# Register your models here.


from .models import * 

admin.site.register(Category)



class ProductImageAdmin(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name", "category", "price")
    inlines = [ProductImageAdmin]




@admin.register(ColorVariation)
class ColorVariationAdmin(admin.ModelAdmin):
    list_display = ("color_name", "price")
    model = ColorVariation


@admin.register(SizeVariation)
class SizeVariationAdmin(admin.ModelAdmin):
    list_display = ("size_name", "price")
    model = SizeVariation



admin.site.register(Product, ProductAdmin)



admin.site.register(ProductImage)