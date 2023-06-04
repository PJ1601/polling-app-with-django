from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self) -> QuerySet[Any]:
        subquery = (
            Question.objects.filter(choice__isnull=False)
            .values("id")
            .filter(id=OuterRef("id"))
            .annotate(count=Count("id"))
            .values("count")
        )
        return (
            Question.objects.filter(pub_date__lte=timezone.now())
            .annotate(choice_count=Subquery(subquery))
            .filter(choice_count__gt=0)
            .order_by("-pub_date")[:5]
        )


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self) -> QuerySet[Any]:
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self) -> QuerySet[Any]:
        """
        Excludes results of questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class VoteHandler:
    def __init__(self, question_id):
        self.question_id = question_id

    def get_question(self):
        return get_object_or_404(Question, pk=self.question_id)

    def vote(self, choice_id):
        question = self.get_question()
        try:
            selected_choice = question.choice_set.get(pk=choice_id)
        except (KeyError, Choice.DoesNotExist):
            return False, question, "You didn't select a choice."
        else:
            selected_choice.votes = F("votes") + 1
            selected_choice.save()
            return True, question, ""


def vote(request, question_id):
    vote_handler = VoteHandler(question_id)
    choice_id = request.POST.get("choice")
    success, question, error_message = vote_handler.vote(choice_id)

    if success:
        return HttpResponseRedirect(reverse("polls:results", args=(question_id,)))
    else:
        return render(
            request,
            "polls/detail.html",
            {"question": question, "error_message": error_message},
        )
