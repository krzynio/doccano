import string
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    PROJECT_CHOICES = (
        ('DocumentClassification', 'document classification'),
        ('SequenceLabeling', 'sequence labeling'),
        ('Seq2seq', 'sequence to sequence'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User)
    project_type = models.CharField(max_length=30, choices=PROJECT_CHOICES)

    def __str__(self):
        return self.name


class Label(models.Model):
    KEY_CHOICES = ((U, c) for U, c in zip(string.ascii_uppercase, string.ascii_lowercase))
    COLOR_CHOICES = ()

    text = models.CharField(max_length=100, unique=True)
    shortcut = models.CharField(max_length=10, unique=True, choices=KEY_CHOICES)
    project = models.ForeignKey(Project, related_name='labels', on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Document(models.Model):
    text = models.TextField()
    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:50]


class Annotation(models.Model):
    prob = models.FloatField(default=0.0)
    manual = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class DocumentAnnotation(Annotation):
    document = models.ForeignKey(Document, related_name='doc_annotations', on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('document', 'user', 'label')


class SequenceAnnotation(Annotation):
    document = models.ForeignKey(Document, related_name='seq_annotations', on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    start_offset = models.IntegerField()
    end_offset = models.IntegerField()

    def clean(self):
        if self.start_offset >= self.end_offset:
            raise ValidationError('start_offset is after end_offset')

    class Meta:
        unique_together = ('document', 'user', 'label', 'start_offset', 'end_offset')


class Seq2seqAnnotation(Annotation):
    document = models.ForeignKey(Document, related_name='seq2seq_annotations', on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        unique_together = ('document', 'user', 'text')
