from django.urls import path

from . import views

app_name = "enquiries"

urlpatterns = [
    path("", views.enquiry_create, name="create"),
    path("history/", views.enquiry_history, name="history"),
    path("history/<str:reference>/", views.enquiry_detail, name="detail"),
    path("history/<str:reference>/quotation/", views.quotation_download, name="quotation"),
    path("sent/<str:reference>/", views.enquiry_success, name="success"),
]
