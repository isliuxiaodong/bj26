from django.conf.urls import url
from . import views
urlpatterns = [
    url('^add$',views.add),
    url('^$',views.index),
    url('^edit$',views.edit),
    url('^delete$',views.delete),
]