from django.urls import path

from . import views

urlpatterns = [
    path('register/welcome', views.RegisterWelcomeView.as_view(), name='register-welcome'),
    path('register/form', views.RegisterWizard.as_view(), name='register-form'),
    path('licence/<int:id>/payment', views.licencePayment, name='licence-payment'),
    path('licence/<int:id>/payed', views.licencePayed, name='licence-payed'),
    path('register/done', views.DoneView.as_view(), name='register-done'),
    path('register/already', views.AlreadyRegisteredView.as_view(), name='register-already'),
    path('logout', views.sso_logout, name='logout'),
    path('', views.ProfileView.as_view(), name='profile'),
]
