from django.test import TestCase

from filter.models import Travel
from filter.utils import CustomFilter


class TestCustomFilter(TestCase):
    fixtures = ['fixtures.json']

    def test_gt_operator_works(self):
        search_phrase = "date gt 2020-02-01"
        allowed_fields = ["date"]

        custom_filter = CustomFilter(
            allowed_fields=allowed_fields,
            phrase=search_phrase
        )
        filters = custom_filter.parse_search_phrase()
        filtered_results = Travel.objects.filter(filters).values_list('id', flat=True)

        expected_results = set([4, 5, 6])

        self.assertTrue(set(filtered_results) == expected_results)

    def test_lt_operator_works(self):
        search_phrase = "date lt 2020-02-01"
        allowed_fields = ["date"]

        custom_filter = CustomFilter(
            allowed_fields=allowed_fields,
            phrase=search_phrase
        )
        filters = custom_filter.parse_search_phrase()
        filtered_results = Travel.objects.filter(filters).values_list('id', flat=True)

        expected_results = set([1, 2])

        self.assertTrue(set(filtered_results) == expected_results)

    def test_ne_operator_works(self):
        search_phrase = "date ne 2020-01-01"
        allowed_fields = ["date"]

        custom_filter = CustomFilter(
            allowed_fields=allowed_fields,
            phrase=search_phrase
        )
        filters = custom_filter.parse_search_phrase()
        filtered_results = Travel.objects.filter(filters).values_list('id', flat=True)

        expected_results = set([2, 3, 4, 5 ,6])

        self.assertTrue(set(filtered_results) == expected_results)

    def test_eq_operator_works(self):
        search_phrase = "distance eq 20"
        allowed_fields = ["distance"]

        custom_filter = CustomFilter(
            allowed_fields=allowed_fields,
            phrase=search_phrase
        )
        filters = custom_filter.parse_search_phrase()
        filtered_results = Travel.objects.filter(filters).values_list('id', flat=True)

        expected_results = set([4])

        self.assertTrue(set(filtered_results) == expected_results)

    def test_and_operator_works(self):
        search_phrase = "distance lt 20 AND date gt 2020-01-01"
        allowed_fields = ["distance", "date"]

        custom_filter = CustomFilter(
            allowed_fields=allowed_fields,
            phrase=search_phrase
        )
        filters = custom_filter.parse_search_phrase()
        filtered_results = Travel.objects.filter(filters).values_list('id', flat=True)

        expected_results = set([2,3])

        self.assertTrue(set(filtered_results) == expected_results)

    def test_or_operator_works(self):
        search_phrase = "distance gt 20 OR date lt 2020-03-02"
        allowed_fields = ["distance", "date"]

        custom_filter = CustomFilter(
            allowed_fields=allowed_fields,
            phrase=search_phrase
        )
        filters = custom_filter.parse_search_phrase()
        filtered_results = Travel.objects.filter(filters).values_list('id', flat=True)

        expected_results = set([1, 2, 3, 4, 5, 6])

        self.assertTrue(set(filtered_results) == expected_results)

    def test_precedence_works(self):
        search_phrase = "(date eq 2016-05-01) AND ((distance gt 20) AND (distance lt 22))"
        allowed_fields = ["distance", "date"]

        custom_filter = CustomFilter(
            allowed_fields=allowed_fields,
            phrase=search_phrase
        )
        filters = custom_filter.parse_search_phrase()
        filtered_results = Travel.objects.filter(filters).values_list('id', flat=True)

        expected_results = set([1, 2, 3, 4, 5, 6])

        self.assertTrue(set(filtered_results) == expected_results)
