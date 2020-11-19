from django.urls import include, path, re_path
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
import web.apps.web_copo.views as views
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('copo/', include('web.apps.web_copo.urls', namespace='copo')),

    path('rest/', include('web.apps.web_copo.rest_urls', namespace='rest')),
    path('api/', include('api.urls', namespace='api')),

    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.index),
    path('', TemplateView.as_view(template_name="index.html"), name='index'),
    path('people/', TemplateView.as_view(template_name="people.html"), name='people')
]

if settings.DEBUG is False:  # if DEBUG is True it will be served automatically
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
