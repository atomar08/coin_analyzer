from django.urls import path

from bitcoin import views

urlpatterns = [
    path('ping/', views.get_ping, name='get_ping'),
    path('bitcoin/price_chart/', views.get_price_chart, name='get_price_chart'),
    # path('ping/', views.ping, name='ping'),
]