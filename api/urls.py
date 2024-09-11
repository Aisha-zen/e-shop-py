from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UserDetailsView
from .views import ProductListView, ProductCreateView, ProductRetrieveView, ProductUpdateView, ProductDestroyView, BulkProductCreateAPI
from .views import RecommenderView, CategoryView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserDetailsView.as_view(), name='user-details'),
    path('products/', ProductListView.as_view(), name='product-list-create'),
    path('products/bulk/', BulkProductCreateAPI.as_view(),
         name='bulk-product-create'),
    # Bulk create products
    path('product/<int:pk>/', ProductRetrieveView.as_view(),
         name='product-detail'),
    path('product/<int:pk>/', ProductCreateView.as_view(),
         name='product-detail'),
    path('product/<int:pk>/', ProductUpdateView.as_view(),
         name='product-detail'),
    path('product/<int:pk>/', ProductDestroyView.as_view(),
         name='product-detail'),

    path('recommend/<str:pk>/', RecommenderView.as_view(), name='recommend'),
    path('categories/', CategoryView.as_view(), name='category-list'),

]
