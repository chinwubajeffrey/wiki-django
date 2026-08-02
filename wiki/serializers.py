from rest_framework import serializers
from .models import Page, Revision

class RevisionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Revision
        fields = ['id', 'page', 'content', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class PageSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'content', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']