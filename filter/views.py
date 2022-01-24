from django.shortcuts import render, HttpResponse

from filter.models import Travel
from filter.utils import CustomFilter

def parse_search_phrase(allowed_fields, search_phrase):
    print(f"allowed_fields = {allowed_fields}")
    print(f"search_phrase = {search_phrase}")
    return {}

def travel_list(request):
    """
    Returns page containing list of all travels along
    with their date and distance.
    """
    phrase = request.GET.get("phrase", "")
    allowed_fields = request.GET.getlist("allowed_fields[]", "")

    custom_filter = CustomFilter(allowed_fields=allowed_fields, phrase=phrase)

    filters = custom_filter.parse_search_phrase()

    travels = Travel.objects.filter(filters)

    return render(request, "index.html", context={"travels": travels})
