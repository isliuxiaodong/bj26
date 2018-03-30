from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from celery import Celery
from tt_goods.models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexCategoryGoodsBanner,IndexPromotionBanner,IndexGoodsBanner
import os
from django.shortcuts import render
import time

app=Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')

# @app.task
# def send_user_active(user):
#     serializer = Serializer(settings.SECRET_KEY, 60 * 10)
#     value = serializer.dumps({'id': user.id}).decode()
#
#     msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
#     send_mail('天天生鲜-账户激活', '', settings.EMAIL_FROM, [user.email], html_message=msg)
#

@app.task
def send_user_active(user):
    # 加密用户编号
    serializer = Serializer(settings.SECRET_KEY, 60 * 60)
    value = serializer.dumps({'id': user.id}).decode()

    # 让用户激活：向注册的邮箱发邮件，点击邮件中的链接，转到本网站的激活地址
    msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
    send_mail('天天生鲜-账户激活', '', settings.EMAIL_FROM, [user.email], html_message=msg)


@app.task
def generate_html():
    time.sleep(2)
    # 查询分类信息
    category_list = GoodsCategory.objects.all()

    # 查询轮播图片
    banner_list = IndexGoodsBanner.objects.all().order_by('index')

    # 查询广告
    adv_list = IndexPromotionBanner.objects.all().order_by('index')

    # 查询每个分类的推荐产品
    for category in category_list:
        # 查询推荐的标题商品，当前分类的，按照index排序的，取前3个
        category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by(
            'index')[0:3]
        # 查询推荐的图片商品
        category.img_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by(
            'index')[0:4]

    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'adv_list': adv_list,
    }
    response = render(None, 'index.html', context)

    # 优化：每次访问数据都一样，为了减少读数据库、渲染模板的消耗，直接将数据保存到文件中
    html = response.content.decode()  # bytes==>str
    # 将html字符串保存到文件中
    with open(os.path.join(settings.GENERATE_HTML, 'index.html'), 'w') as f1:
        f1.write(html)

