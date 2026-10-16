from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("", views.service_list, name="list"),
    path("request/", views.request_create, name="request"),
    path("my-requests/", views.buyer_list, name="buyer_list"),
    path("technician/", views.technician_list, name="technician_list"),
    path("technician/<int:pk>/", views.technician_update, name="technician_update"),
    path("technician/<int:pk>/claim/", views.technician_claim, name="technician_claim"),
]
