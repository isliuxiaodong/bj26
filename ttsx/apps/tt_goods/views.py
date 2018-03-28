from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
# Create your views here.
def fdfs_test(request):
    category = GoodsCategory.objects.get(pk=1)
    context = {'category': category}
    print(type(category.image))
    # django.db.models.fields.files.ImageFieldFile
    return render(request, 'fdfs_test.html', context)


def index(request):
    # 查询分类信息
    category_list = GoodsCategory.objects.all()

    # 查询轮播图片
    banner_list = IndexGoodsBanner.objects.all().order_by('index')

    # 查询广告
    adv_list = IndexPromotionBanner.objects.all().order_by('index')

    # 查询每个分类的推荐产品
    for category in category_list:
        # 查询推荐的标题商品，当前分类的，按照index排序的，取前3个
        category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by('index')[0:3]
        # 查询推荐的图片商品
        category.img_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by('index')[0:4]

    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'adv_list': adv_list,
    }
    return render(request, 'index.html', context)
