from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    ('^optimize/$', views.optimize),
)
