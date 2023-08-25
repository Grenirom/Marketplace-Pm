from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response

from account.permissions import IsAuthorOrAdmin
from .models import Order
from .serializers import OrderSerializer, UserOrderListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ('create', 'list', 'retrieve'):
            return [IsAuthorOrAdmin(), ]
        elif self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser(), ]

    def list(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            all_orders = Order.objects.all()
            serializer = UserOrderListSerializer(all_orders, many=True)
            return Response(serializer.data)
        elif self.request.user.is_authenticated:
            user_orders = Order.objects.filter(user=request.user)
            serializer = UserOrderListSerializer(user_orders, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Возвращаем товар обратно на склад
        for order_item in instance.items.all():
            product = order_item.product
            product.quantity += order_item.quantity
            product.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)