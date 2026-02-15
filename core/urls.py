from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('submit-inquiry/', views.submit_inquiry, name='submit_inquiry'),
    path('submit-damage/', views.submit_damage, name='submit_damage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('p/<slug:slug>/', views.menu_item_page, name='menu_item_page'),
    path('insurance/<slug:slug>/', views.insurance_detail, name='insurance_detail'),
    path('info/<slug:slug>/', views.insurance_info_detail, name='insurance_info_detail'),
    path('company/<slug:slug>/', views.company_detail, name='company_detail'),
    
    path('api/check-user/', views.check_user_api, name='check_user'),
    path('api/auth-user/', views.auth_user_api, name='auth_user'),
    
    path('logout/', views.user_logout, name='logout'),
    path('buy/<slug:card_slug>/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('payment/verify/<int:order_id>/', views.fake_payment, name='fake_payment'),
    path('insurance/', views.insurance_form, name='insurance_form'),
    path('api/get-models/', views.get_models, name='get_models'),
    path('api/get-motor-models/', views.get_motor_models, name='get_motor_models'),
    path('api/submit-order/', views.submit_order, name='submit_order'),
    path('api/calculate-prices/', views.calculate_prices_api, name='calculate_prices_api'),
]