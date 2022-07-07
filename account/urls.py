from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import Login, Signup

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', Signup.as_view(), name='signup'),
]
