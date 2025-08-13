"""
URL configuration for turopamiestilo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path as url # from django.conf.urls import url # se usaba en la version 3.4
from django.contrib import admin
import django.views.static

from appturopamiestilo import views, perfil, modulo, persona, usuario, parroquia, empresa
from turopamiestilo import settings

urlpatterns = []
if settings.DEBUG:
    urlpatterns = [
        url(r'^turopamiestilo/static/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.STATIC_ROOT}),
        url(r'^turopamiestilo/media/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT}),
    ]

urlpatterns += {
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.panel),
    url(r'^login', views.login_user),
    url(r'^logout$', views.logout_user),
    url(r'^perfil', perfil.view),
    url(r'^modulo', modulo.view),
    url(r'^persona', persona.view),
    url(r'^usuario', usuario.view),
    url(r'^parroquia', parroquia.view),
    url(r'^empresa', empresa.view),



}
