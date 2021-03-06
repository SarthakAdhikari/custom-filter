from django.shortcuts import render, HttpResponse
from django.core.exceptions import FieldError

from filter.models import Travel
from filter.utils import CustomFilter


def dashboard(request):
    """
    Returns page containing list of all travels along
    with their date and distance.
    """
    context = {}
    phrase = request.GET.get("phrase", "")
    allowed_fields = request.GET.getlist("allowed_fields[]", "")

    custom_filter = CustomFilter(allowed_fields=allowed_fields, phrase=phrase)

    try:
        filters = custom_filter.parse_search_phrase()
        travels = Travel.objects.filter(filters)
        context.update({"travels": travels})
        context.update({"current_phrase": phrase})
    except (FieldError, ValueError) as e:
        context.update({"error": str(e)})

    return render(request, "dashboard.html", context)

def homepage(request):
    """
    Returns page containing list of all travels along
    with their date and distance.
    """
    return render(request, "index.html")
