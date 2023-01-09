from django.db import models
from django.contrib import admin


class Quandary(models.Model):
    quandary_text = models.CharField(max_length=255)
    landscape = models.ForeignKey('Landscape', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.quandary_text


class Answer(models.Model):
    answer_text = models.CharField(max_length=255)
    quandary = models.ForeignKey(Quandary, related_name='answers', on_delete=models.CASCADE)
    child_quandary = models.ForeignKey(Quandary, related_name='parent_answer', on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.answer_text


class Hero(models.Model):
    moniker = models.CharField(max_length=255)
    portrait = models.ForeignKey('Portrait', related_name='heroes', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.moniker


class Landscape(models.Model):
    image = models.ImageField(upload_to='landscapes/', null=True, blank=True)
    keywords = models.TextField(null=False)

    def __str__(self):
        return self.keywords


class Portrait(models.Model):
    image = models.ImageField(upload_to='portraits/', null=True, blank=True)
    keywords = models.TextField(null=False)

    def __str__(self):
        return self.keywords
