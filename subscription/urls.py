from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.home, name='home'),
    path('join', views.join, name='join'),
    path('checkout', views.checkoutt, name='checkout'),
    path('success', views.success, name='success'),
    path('cancel', views.cancel, name='cancel'),
    path('updateaccounts', views.updateaccounts, name='updateaccounts'),
]
