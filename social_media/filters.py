from django.db.models import QuerySet, Q
from django.http import QueryDict
from rest_framework.filters import BaseFilterBackend


class HashtagSearchBackend(BaseFilterBackend):

    @staticmethod
    def get_q_filters_from_query_params(query_params: QueryDict) -> Q:
        q = Q()
        for hashtag in query_params.getlist("hashtags"):
            q |= Q(content__icontains=f"#{hashtag}")
        return q

    def filter_queryset(self, request, queryset, view) -> QuerySet:
        filters = self.get_q_filters_from_query_params(request.query_params)
        if filters:
            return queryset.filter(filters)
        return queryset
