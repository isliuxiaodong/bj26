from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(GoodsCategory)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexCategoryGoodsBanner)
admin.site.register(IndexPromotionBanner)
admin.site.register(IndexGoodsBanner)