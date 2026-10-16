from django.urls import path

from . import views

app_name = "manager"

urlpatterns = [
    path("", views.index, name="index"),
    path("enquiries/", views.enquiry_list, name="enquiry_list"),
    path("enquiries/<str:reference>/", views.enquiry_detail, name="enquiry_detail"),
    path("services/", views.service_list, name="service_list"),
    path("services/<int:pk>/", views.service_detail, name="service_detail"),
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
]
