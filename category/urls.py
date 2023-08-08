from django.urls import path

from category.views import CategoryCreateListView, CategoryDetailView, CategoryPhotoListCreateView, \
    CategoryPhotoDetailView

urlpatterns = [
    path('', CategoryCreateListView.as_view(), name='category-list-create'),
    path('<slug:slug>/', CategoryDetailView.as_view(), name='category-detail-update'),
    path('<slug:slug>/photos_desc/', CategoryPhotoListCreateView.as_view(), name='category-photo-list-create'),
    path('<slug:slug>/photos_desc/<int:pk>/', CategoryPhotoDetailView.as_view(), name='category-photo-detail-update'),
]