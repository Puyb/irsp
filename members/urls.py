from django.urls import path

from . import views

urlpatterns = [
    path('register/welcome', views.RegisterWelcomeView.as_view(), name='register-welcome'),
    path('register/form', views.RegisterWizard.as_view(), name='register-form'),
    path('licence/<int:id>/payment', views.licencePayment, name='licence-payment'),
    path('', views.ProfileView.as_view(), name='profile'),
]
