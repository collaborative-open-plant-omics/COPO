from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

import web.apps.web_copo.views as views
from web.landing import views as landing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('copo/', include('web.apps.web_copo.urls', namespace='copo')),

    path('rest/', include('web.apps.web_copo.rest_urls', namespace='rest')),
    path('api/', include('api.urls', namespace='api')),

    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.index),
    path('', landing_views.index, name='index'),
    path('about/', TemplateView.as_view(template_name="about.html"), name='about'),
    path('people/', TemplateView.as_view(template_name="people.html"), name='people'),
    path('dtol/', TemplateView.as_view(template_name="dtol.html"), name='dtol'),
    path('news/', TemplateView.as_view(template_name="news.html"), name='news'),
    path('manifests/', TemplateView.as_view(template_name="manifests.html"), name='manifests')
]

handler404 = views.handler404
handler500 = views.handler500

if settings.DEBUG is False:  # if DEBUG is True it will be served automatically
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
