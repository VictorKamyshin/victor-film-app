"""tp_laboratory_task URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin
from filmApp import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^film_card/.*', views.film_card_page, name='film_card'),
    url(r'^authorisation/.*', views.authorisation_page, name='authorisation'),

    url(r'^registration/.*', views.registration_page, name='registration'),
    url(r'^registration_confirm/.*', views.register_confirm, name='registration_confirm'),

    url(r'^create_film_card/.*', views.create_film, name='create_film'),
    url(r'^edit_film_card/.*$', views.edit_film, name='edit_film'),
    url(r'^delete_film/.*$', views.delete_film, name='delete_film'),
    url(r'^restore_film/.*$', views.restore_film, name='restore_film'),

    url(r'^main/.*$', views.main_page, name='main_page'),
    url(r'^$', views.main_page, name='main_page'),


    url(r'^profile_edit/.*$', views.profile_edit_page, name='profile'),
    url(r'^profile_view/.*$', views.profile_view_page, name='profile_view'),

    url(r'^logout/.*$',views.user_logout, name='user_logout'),
    url(r'^appraisal/.*$', views.film_card_appraisal, name='appraisal'),

    url(r'^film_comment/.*$', views.film_comment, name='film-comment'),
    url(r'^edit_comment/.*$', views.edit_comment, name='edit_comment'),
    url(r'^delete_comment/.*$',views.delete_comment, name='delete_comment'),
    url(r'^restore_comment/.*$', views.restore_comment, name='restore_comment'),

    url(r'^api/film_list/.*$', views.api_film_list, name='api_film_list'),
    url(r'^api/film_card/.*$', views.api_film_card, name='api_film_card'),

]
