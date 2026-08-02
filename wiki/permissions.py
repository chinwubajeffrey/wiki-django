from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # obj is a Page: check .owner
        # obj is a Revision: check .page.owner
        owner = getattr(obj, 'owner', None) or obj.page.owner
        return owner == request.user
    