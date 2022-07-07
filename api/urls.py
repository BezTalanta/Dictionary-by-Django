from django.urls import path
from .views import MenuPage, ApiPage, WordViewSet, WordAPIView


app_name = 'doc'
urlpatterns = [
    path('', MenuPage.as_view(), name='menu'),
    path('api/', ApiPage.as_view(), name=''),
    path('api/list/', WordViewSet.as_view({'get': 'own_list'}), name='api'),
    # path('api/create/', WordViewSet.as_view({'get': 'create_word'}), name='api'),
    # path('api/list/', WordAPIView.as_view(), name='api'),
]