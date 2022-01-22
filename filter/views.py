from django.shortcuts import render, HttpResponse

from filter.models import Travel

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

    filters = parse_search_phrase(allowed_fields, phrase)

    travels = Travel.objects.filter(**filters)

    return render(request, "index.html", context={"travels": travels})
