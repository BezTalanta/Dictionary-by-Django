from django.urls import path
# from .views import HomeView
from django.views import View
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name='home/home_page.html'), name='home'),
    # path('home/', HomeView.as_view(), name='home'),
]
