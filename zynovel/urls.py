"""zynovel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.bookshelf),
    url(r'^manager/$', views.manager),
    url(r'^manager/search/$', views.search),
    url(r'^manager/add/$', views.manager),
    url(r'^manager/cachechapter/$', views.cachechapter),
    url(r'^book/$', views.bookshelf),
    url(r'^book/(?P<bookid>\d+)/$', views.book),
    url(r'^book/(?P<bookid>\d+)/(?P<chapterid>\d+).html', views.chapter),
    url(r'^downbook/(?P<bookid>\d+)/$', views.downbook),
]
