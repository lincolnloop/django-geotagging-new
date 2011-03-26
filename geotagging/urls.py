from django.conf.urls.defaults import *
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
    ('^optimize/$', views.optimize),
    ('^map/$', TemplateView.as_view(template_name='geotagging/map.html')),
)
