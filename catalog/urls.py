from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("saved/", views.saved_products, name="saved"),
    path("technical/", views.technical, name="technical"),
    path("documents/<int:pk>/download/", views.document_download, name="document_download"),
    path("<slug:slug>/", views.product_detail, name="detail"),
    path("<slug:slug>/save/", views.toggle_save, name="toggle_save"),
]
