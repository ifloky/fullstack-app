from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("reports/", views.reports, name="reports"),
    path('add_personal_report/', views.add_personal_report, name='add_personal_report'),
    path('add_day_report/', views.add_day_report, name='add_day_report'),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path("rocket/", views.rocket, name="rocket"),
    path("payment/", views.payment, name="payment"),
    path('ip_info/', views.info_by_ip, name='ip_info'),
]
