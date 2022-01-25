from django.urls import path

from filter.views import dashboard, homepage

urlpatterns = [
    path('', homepage),
    path('dashboard/', dashboard),
]
