import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin


# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    # string represention of objects in Question
    def __str__(self) -> str:
        return self.question_text

    @admin.display(boolean=True, ordering="pub_date", description="Published recently")
    def was_published_recently(self):
        now = timezone.now()
        return now >= self.pub_date >= now - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=250)
    votes = models.IntegerField(default=0)

    # string representation of objects in Choice
    def __str__(self) -> str:
        return self.choice_text
