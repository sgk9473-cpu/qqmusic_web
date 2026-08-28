"""
URL configuration for musicweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from music.views import home, song_list, song_detail, singer_detail, singer_list, search

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', home, name='home'),
    
    path("songs/", song_list, name="song_list"),
    path("songs/<int:song_id>/", song_detail, name="song_detail"),
    
    path("singers/", singer_list, name="singer_list"),
    path("singers/<int:singer_id>/", singer_detail, name="singer_detail"),
    
    path("search/", search, name="search"),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)