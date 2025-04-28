from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import healthcheck, log_error


# Configure error handlers
handler404 = 'settings.views.handle_404'
handler500 = 'settings.views.handle_500'

urlpatterns = [
    path("admin/defender/", include("defender.urls")),
    path("admin/", admin.site.urls),
    path("openapi/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("healthcheck/", healthcheck),
    
    path("log_error/", log_error),
    path('api/', include('user.urls')),
    path('', include('barter.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# #EXAMPLES
# from .aboba_examples import (
#     basic_example,
#     json_example,
#     multiple_response_types,
#     complex_params_example,
#     nested_arrays_example,
#     custom_serializer_fields,
#     auth_required_example,
#     better_serializer_example,
#     UserViewSet,
#     ProductViewSet
# )
# router = DefaultRouter()
# router.register(r'api/users', UserViewSet, basename='user')
# router.register(r'api/products', ProductViewSet, basename='product')
# urlpatterns += router.urls
# urlpatterns += [
#     path("examples/basic/", basic_example),
#     path("examples/json/", json_example),
#     path("examples/multiple-responses/", multiple_response_types),
#     path("examples/complex-params/", complex_params_example),
#     path("examples/nested-arrays/", nested_arrays_example),
#     path("examples/custom-fields/", custom_serializer_fields),
#     path("examples/auth-required/", auth_required_example),
#     path("examples/better-serializer/", better_serializer_example),
# ]
