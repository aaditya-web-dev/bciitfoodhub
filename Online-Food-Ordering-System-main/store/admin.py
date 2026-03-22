from django.contrib import admin
from .models import Food, Order, OrderItem

# ===== FOOD MODEL =====
@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 10

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0   # number of empty forms shown
    readonly_fields = []


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)

    def total_price(self, obj):
        return sum(item.food.price * item.quantity for item in obj.items.all())

    total_price.short_description = 'Total Price'


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'order', 'food', 'quantity')
#     search_fields = ('food__name',)
# admin.site.register(Order);
admin.site.site_header = "BCIIT FOODHUB"
admin.site.site_title = "BCIIT FOODHUB"
admin.site.index_title = "Welcome to Dashboard"




























































# ===== ORDER MODEL =====
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'total_price', 'status', 'created_at')
#     list_display_links = ('id',)
#     list_filter = ('status', 'created_at')
#     search_fields = ('user__username',)
#     ordering = ('-created_at',)
#     list_per_page = 10

# ===== ORDER ITEM MODEL =====
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'order', 'food', 'quantity')
#     list_display_links = ('id',)
#     search_fields = ('user__username', 'food__name')
#     list_per_page = 10

#     def subtotal(self, obj):
#         return obj.subtotal()
#     subtotal.short_description = 'Subtotal'
