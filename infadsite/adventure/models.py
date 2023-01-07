from django.db import models
from django.contrib import admin


class Quandary(models.Model):
    quandary_text = models.CharField(max_length=255)
    description = models.CharField(max_length=1023, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.quandary_text

    @admin.display(
        boolean=True,
        ordering='description',
        description='Flavor text?',
    )
    def has_description(self):
        return self.description != ""


class Answer(models.Model):
    quandary = models.ForeignKey(Quandary, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.answer_text


class Hero(models.Model):
    moniker = models.CharField(max_length=255)
    answers_given = models.ManyToManyField(Answer, related_name='heroes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.moniker