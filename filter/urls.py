from django.urls import path

from filter.views import travel_list

urlpatterns = [
    path('', travel_list),
    # path('dashboard/', travel_list),
]
