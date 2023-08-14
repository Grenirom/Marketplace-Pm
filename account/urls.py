from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter
from account.views import UserViewSet


router = SimpleRouter()
router.register('', UserViewSet)

seller_router = SimpleRouter()
seller_router.register(r'seller-profiles', views.SellerProfileViewSet)

user_profile_router = SimpleRouter()
user_profile_router.register(r'user-profiles', views.UserProfileViewSet, basename='userprofile')

seller_pending_router = SimpleRouter()
seller_pending_router.register(r'pending-profiles', views.SellerAllView, basename='pendingprofile')


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('refresh/', views.RefreshView.as_view()),
    path('', include(router.urls)),
    path('', include(seller_router.urls)),
    path('', include(user_profile_router.urls)),
    path('', include(seller_pending_router.urls)),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # path('<int:pk>/', views.UserUpdateViewSet.as_view({'patch': 'update'})),
    # path('change-password/', views.ChangePasswordView.as_view()),
    path('approve-seller/<int:pk>/', views.ApproveSellerView.as_view()),
    path('seller-reg/', views.SellerProfileCreateView.as_view()),
]

