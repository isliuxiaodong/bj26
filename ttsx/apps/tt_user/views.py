from django.shortcuts import render, redirect
from django.views.generic import View
from .models import User
import re
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from celery_tasks.tasks import send_user_active
from django.contrib.auth import authenticate, login


# Create your views here.
class Registerview(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        dict = request.POST
        uname = dict.get('user_name')
        pwd = dict.get('pwd')
        cpwd = dict.get('cpwd')
        email = dict.get('email')
        uallow = dict.get('allow')

        context = {
            'uname': uname,
            'pwd': pwd,
            'email': email,
            'cpwd': cpwd,
            'err_msg': ''
        }
        if uallow is None:
            context['err_msg'] = '请接受协议'
            return render(request, 'register.html', context)

        if not all([uname, pwd, cpwd, email]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'register.html', context)

        if pwd != cpwd:
            context['err_msg'] = '两次密码不一致'
            return render(request, 'register.html', context)

        if User.objects.filter(username=uname).count() > 0:
            context['err_msg'] = '用户名已存在'
            return render(request, 'register.html', context)

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['err_msg'] = '邮箱格式不正确'
            return render(request, 'register.html', context)

        if User.objects.filter(email=email).count() > 0:
            context['err_msg'] = '邮箱已被注册'
            return render(request, 'register.html', context)

        user = User.objects.create_user(uname, email, pwd)
        user.is_active = False
        user.save()

        serializer = Serializer(settings.SECRET_KEY, 60 * 10)
        value = serializer.dumps({'id': user.id}).decode()

        msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
        send_mail('天天生鲜-账户激活', '', settings.EMAIL_FROM, [email], html_message=msg)

        # send_user_active.delay(user)

        return HttpResponse('注册成功,请到邮箱激活账号！')


def active(request, value):
    try:

        serializer = Serializer(settings.SECRET_KEY)
        dict = serializer.loads(value)
    except SignatureExpired as e:
        return HttpResponse('链接已过期')

    uid = dict.get('id')
    user = User.objects.get(pk=uid)
    user.is_active = True
    user.save()

    return redirect('/user/login')


def exists(request):
    uname = request.GET.get('uname')
    email = request.GET.get('email')
    if uname is not None:
        result = User.objects.filter(username=uname).count()

    if email is not None:
        result = User.objects.filter(email=email).count()

    return JsonResponse({'result': result})


class LoginView(View):
    def get(self, request):
        uname = request.COOKIES.get('uname', '')
        context = {
            'title': '登录',
            'uname': uname
        }
        return render(request, 'login.html', context)

    def post(self, request):
        dict = request.POST
        uname = dict.get('username')
        upwd = dict.get('pwd')
        remember = dict.get('remember')

        context = {
            'uname': uname,
            'upwd': upwd,
            'err_msg': '',
            'title': '登录处理'
        }

        if not all([uname, upwd]):
            context['err_msg'] = '请填写完整信息'
            return render(request, 'login.html', context)

        user = authenticate(username=uname, password=upwd)

        if user is None:
            context['err_msg'] = '用户名或密码错误，请重试'
            return render(request, 'login.html', context)
        if not user.is_active:
            context['err_msg'] = '请先到邮箱中激活'
            return  render(request, 'login.html', context)

        login(request, user)

        response = redirect('/user/info')

        if remember is None:
            response.delete_cookie('uname')

        else:
            response.set_cookie('uname', uname, expires=60 * 60)

        return response
