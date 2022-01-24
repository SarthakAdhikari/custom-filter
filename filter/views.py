from django.shortcuts import render, HttpResponse
from django.core.exceptions import FieldError

from filter.models import Travel
from filter.utils import CustomFilter


def travel_list(request):
    """
    Returns page containing list of all travels along
    with their date and distance.
    """
    context = {}
    phrase = request.GET.get("phrase", "")
    allowed_fields = request.GET.getlist("allowed_fields[]", "")

    custom_filter = CustomFilter(allowed_fields=allowed_fields, phrase=phrase)

    filters = custom_filter.parse_search_phrase()

    try:
        travels = Travel.objects.filter(filters)
        context.update({"travels": travels})
    except (FieldError, ValueError) as e:
        context.update({"error": str(e)})

    return render(request, "index.html", context)
