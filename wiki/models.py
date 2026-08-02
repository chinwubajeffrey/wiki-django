from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Revision(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='revisions')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='revisions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Revision of {self.page.title} at {self.created_at}"