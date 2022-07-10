from django.urls import path
from .views import (
    WordListView,
    AddWordView,
    DetailWordView,
    ModelRunView,
    TestForms,
)

urlpatterns = [
    path('', WordListView.as_view(), name='dict-list'),
    path('add/', AddWordView.as_view(), name='add-word'),
    path('<int:id>/', DetailWordView.as_view(), name='detail-word'),
    path('run/', ModelRunView.as_view(), name='run'),
    path('runm/', ModelRunView.as_view(), name='runm'),
    path('test/', TestForms.as_view(), name='test'),
    # path('runc/', RunView.as_view(), name='run'),
    # path('runs/', RunView.as_view(), name='run'),
]
