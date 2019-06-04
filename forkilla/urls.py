from django.conf.urls import url

from . import views

listOfAddresses = ["https://sd2019-forkillaf1.herokuapp.com"]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^restaurants/(?P<city>.*)/(?P<category>.*)/$', views.restaurants, name='restaurants'),
    url(r'^restaurants/(?P<city>.*)/$', views.restaurants, name='restaurants'),
    url(r'^restaurants/$', views.restaurants, name='restaurants'),
    url(r'^reservation/$', views.reservation, name='reservation'),
    url(r'^reviews/$', views.reviews, name='reviews'),
    url(r'^restaurant/(?P<restaurant_number>.*)/$', views.details, name='restaurant'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^admin/forkilla/restaurant/add/$', views.addrestaurant, name='addrestaurant'),
    url(r'^reservations/$', views.reservationlist, name='reservations'),
    url(r'^comparator/$', views.comparator, {'ips': listOfAddresses}, name='comparator'),
]