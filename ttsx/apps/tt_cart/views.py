from django.shortcuts import render
from django.http import JsonResponse,Http404
from tt_goods.models import GoodsSKU
import json
from django_redis import get_redis_connection

# Create your views here.
def add(request):

    if request.method != 'POST':
        return Http404()
    dict=request.POST
    sku_id=dict.get('sku_id')
    count=int(dict.get('count',0))

    if GoodsSKU.objects.filter(id=sku_id).count()<=0:
        return JsonResponse({'status':2})
    if count<=0:
        return JsonResponse({'status':3})
    if count>=5:
        count=5

    if request.user.is_authenticated():
        redis_client=get_redis_connection()
        key='cart%d'%request.user.id
        if redis_client.hexists(key,sku_id):
            count1=int(redis_client.hget(key,sku_id))
            count2=count
            count0=count1+count2
            if count0>5:
                count0=5
            redis_client.hset(key,sku_id,count0)
        else:
            redis_client.hset(key,sku_id.count)

        total_count=0
        for v in redis_client.hvals(key):
            total_count+=int(v)
        response = JsonResponse({'status': 1,'total_count':total_count})


    else:
        cart_dict = {}
        cart_str=request.COOKIES.get('cart')
        if cart_str:
            cart_dict=json.loads(cart_str)
        if sku_id in cart_dict:
            count1 = cart_dict[sku_id]
            count0 = count + count1
            if count0>5:
                count0=5
            cart_dict[sku_id]= count0
        else:
            cart_dict[sku_id]=count

        total_count=0
        for k, v in cart_dict.items():
            total_count+=v
        cart_str = json.dumps(cart_dict)
        response = JsonResponse({'status': 1,'total_count':total_count})
        response.set_cookie('cart',cart_str,expires=60*60*24*7)

    return response

def index(request):
    sku_list = []
    if request.user.is_authenticated():
        redis_client=get_redis_connection()
        key='cart%d'%request.user.id
        id_list=redis_client.hkeys(key)
        for id1 in id_list:
            sku=GoodsSKU.objects.get(pk=id1)
            sku.cart_count=int(redis_client.hget(key,id1))
            sku_list.append(sku)
    else:
        cart_str=request.COOKIES.get('cart')
        if cart_str:
            cart_dict=json.loads(cart_str)

            for k,v in cart_dict.items():
                sku=GoodsSKU.objects.get(pk=k)
                sku.cart_count=v
                sku_list.append(sku)

    context={
        'title':'购物车',
        'sku_list':sku_list,

    }

    return render(request,'cart.html',context)
