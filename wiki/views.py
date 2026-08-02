from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Page, Revision
from .serializers import PageSerializer, RevisionSerializer
from .permissions import IsOwnerOrReadOnly


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # owner comes from the logged-in user, never from the request body
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # every update creates a snapshot of the OLD content before overwriting
        page = self.get_object()
        Revision.objects.create(
            page=page,
            content=page.content,
            created_by=self.request.user
        )
        serializer.save()

    @action(detail=True, methods=['get'])
    def revisions(self, request, pk=None):
        page = self.get_object()
        revisions = page.revisions.all()
        serializer = RevisionSerializer(revisions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='revisions/(?P<revision_id>[^/.]+)/restore')
    def restore_revision(self, request, pk=None, revision_id=None):
        page = self.get_object()
        try:
            revision = page.revisions.get(id=revision_id)
        except Revision.DoesNotExist:
            return Response({'detail': 'Revision not found for this page.'}, status=404)

        # ownership check: only the page owner can restore
        if page.owner != request.user:
            return Response({'detail': 'Not permitted.'}, status=403)

        # snapshot current content before overwriting, same as a normal edit
        Revision.objects.create(page=page, content=page.content, created_by=request.user)
        page.content = revision.content
        page.save()

        return Response(PageSerializer(page).data)