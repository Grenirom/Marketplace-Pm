from django.urls import path

from category.views import CategoryCreateListView, CategoryDetailView


urlpatterns = [
    path('', CategoryCreateListView.as_view(), name='category-list-create'),
    path('<slug:slug>/', CategoryDetailView.as_view(), name='category-detail-update')
]