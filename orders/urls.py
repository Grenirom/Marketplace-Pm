from django.urls import path, include
from rest_framework.routers import SimpleRouter

from orders import views

order_router = SimpleRouter()
order_router.register('', views.OrderViewSet)

urlpatterns = [
    path('', include(order_router.urls))
]