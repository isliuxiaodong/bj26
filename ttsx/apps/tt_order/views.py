from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tt_goods.models import *
from django_redis import get_redis_connection
from django.http import Http404,JsonResponse
from .models import *
import uuid
from django.db import transaction
from django.db.models import F
# Create your views here.

@login_required
def index(request):
    sku_ids=request.GET.getlist('sku_id')
    add_list=request.user.address_set.all()
    sku_list=[]
    redis_client=get_redis_connection()
    key='cart%d'%request.user.id
    for sku_id in sku_ids:
        sku=GoodsSKU.objects.get(pk=sku_id)
        sku.cart_count=int(redis_client.hget(key,sku_id))
        sku_list.append(sku)
    context={
        'title':'提交订单',
        'addr_list':add_list,
        'sku_list':sku_list,
    }

    return render(request,'place_order.html',context)

@login_required
@transaction.atomic
def handle(request):
    if request.method != 'POST':
        return Http404()

    # 接收数据
    dict = request.POST
    addr_id = dict.get('addr_id')
    pay_style = dict.get('pay_style')
    sku_ids = dict.get('sku_ids')  # '1,2,3,'

    # 验证数据是否存在
    if not all([addr_id, pay_style, sku_ids]):
        return JsonResponse({'status': 2})

    # 处理
    '''
    1.创建订单对象
    2.遍历所有的商品信息，判断库存是否足够
    3.如果足够则继续处理
        3.1创建详细数据
        3.2修改商品库存、销量
        3.3删除购物车数据
        3.4计算总价、总数量
    4.如果不足则返回
    '''
    # 开启事务
    sid = transaction.savepoint()

    # 1.创建订单对象
    order_info = OrderInfo()
    order_info.order_id = str(uuid.uuid1())
    order_info.user = request.user
    order_info.address_id = int(addr_id)
    order_info.total_count = 0
    order_info.total_amount = 0
    order_info.trans_cost = 10
    order_info.pay_method = int(pay_style)
    order_info.save()

    # 构造redis的连接与键
    redis_client = get_redis_connection()
    key = 'cart%d' % request.user.id

    # 2.遍历所有的商品信息，判断库存是否足够
    is_ok = True
    sku_ids = sku_ids.split(',')  # '1,2,3,'==>[1,2,3,]
    sku_ids.pop()
    total_count = 0
    total_amount = 0
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(pk=sku_id)
        cart_count = int(redis_client.hget(key, sku_id))
        # if sku.stock >= cart_count:
        #     # 3.如果足够则继续处理
        #     # 3.1创建详细数据
        #     order_goods = OrderGoods()
        #     order_goods.order = order_info
        #     order_goods.sku = sku
        #     order_goods.count = cart_count
        #     order_goods.price = sku.price
        #     order_goods.save()
        #     # 3.2修改商品库存、销量
        #     sku.stock -= cart_count
        #     sku.sales += cart_count
        #     sku.save()
        #     #3.4计算总价、总数量
        #     total_count+=cart_count
        #     total_amount+=sku.price*cart_count
        # else:
        #     # 4.如果不足则返回
        #     is_ok = False
        #     break
        # 加入乐观锁,返回值表示受影响的行数
        result = GoodsSKU.objects.filter(pk=sku_id, stock__gte=cart_count).update(stock=F('stock') - cart_count,sales=F('sales') + cart_count)
        if result:
            # 库存足够，购买成功
            # 3.1创建详细数据
            order_goods = OrderGoods()
            order_goods.order = order_info
            order_goods.sku = sku
            order_goods.count = cart_count
            order_goods.price = sku.price
            order_goods.save()
            # 3.4计算总价、总数量
            total_count += cart_count
            total_amount += sku.price * cart_count
        else:
            # 库存不足，购买失败
            is_ok = False
            break

    if is_ok:
        # 保存总数量、总价
        order_info.total_count = total_count
        order_info.total_amount = total_amount
        order_info.save()

        # 此逻辑表示整个循环都正常运行完成，数据有效
        transaction.savepoint_commit(sid)

        # 所有的nosql都不支持事务，所以操作完成后再删除redis中的数据
        # 3.3删除购物车数据
        for sku_id in sku_ids:
            redis_client.hdel(key, sku_id)

        return JsonResponse({'status': 1})
    else:
        # 当前逻辑表示某个商品库存不足，之前成功的数据库操作都放弃
        transaction.savepoint_rollback(sid)

        return JsonResponse({'status': 3})
