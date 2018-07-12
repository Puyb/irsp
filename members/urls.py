from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('2/', views.RegisterWizard.as_view(), name='registration_step2'),
]
