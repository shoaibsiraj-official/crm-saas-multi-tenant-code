"""
clients/urls.py

Router registration for the Clients app.

Usage — add to config/urls.py:

    from django.urls import path, include

    urlpatterns = [
        ...
        path("api/", include("clients.urls")),
    ]

This exposes:
    GET    /api/clients/          — list
    POST   /api/clients/          — create
    GET    /api/clients/<pk>/     — retrieve
    PATCH  /api/clients/<pk>/     — partial update
    DELETE /api/clients/<pk>/     — destroy

Note: DefaultRouter also generates a browsable API root at /api/clients/.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClientViewSet


# ── Router ────────────────────────────────────────────────────────────────

router = DefaultRouter()
router.register(r"clients", ClientViewSet, basename="client")


# ── Wire the router into the app's URL namespace ──────────────────────────

# Map ViewSet methods explicitly because ViewSet (not ModelViewSet)
# requires us to declare which HTTP verbs are active.
# DefaultRouter handles this automatically when using ModelViewSet,
# but with a plain ViewSet we bind the actions on the router registration
# using the `get_extra_actions` mechanism — or we can wire it manually here.

# Explicit manual wiring for a plain ViewSet (required since we're not
# subclassing ModelViewSet):
from .views import ClientViewSet as CV

client_list   = CV.as_view({"get": "list",   "post": "create"})
client_detail = CV.as_view({
    "get":    "retrieve",
    "patch":  "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("clients/",         client_list,   name="client-list"),
    path("clients/<uuid:pk>/", client_detail, name="client-detail"),
]

# ── (Optional) If you prefer the router-generated URLs, swap the above
#    urlpatterns with these lines and change ViewSet to ModelViewSet:
#
#    urlpatterns = [
#        path("", include(router.urls)),
#    ]