from django.shortcuts import render
from .models import Restaurant
from .models import Reservation
from .models import ViewedRestaurants
from .models import Review
from .models import RestaurantInsertDate
from .forms import ReservationForm
from .forms import ReviewForm , ComparatorForm
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import RestaurantSerializer, ReviewSerializer
from .permissions import IsOwnerOrReadOnly


def _check_session(request):
    if "viewedrestaurants" not in request.session:
        viewedrestaurants = ViewedRestaurants()
        viewedrestaurants.save()
        request.session["viewedrestaurants"] = viewedrestaurants.id_vr
    else:
        viewedrestaurants = ViewedRestaurants.objects.get(id_vr=request.session["viewedrestaurants"])
    return viewedrestaurants

def index(request):
    restaurants_by_city = Restaurant.objects.filter(is_promot="True")
    promoted = True
    viewedrestaurants = _check_session(request)
    context = {
        'restaurants': restaurants_by_city,
        'user_name': request.user.username,
        'promoted': promoted,
        'admin': request.user.is_superuser,
        'viewedrestaurants': viewedrestaurants,
        'logged': request.user.is_authenticated(),
    }
    return render(request, 'forkilla/restaurants.html', context)


def restaurants(request, city="", category = ""):
    if request.GET.get('search_box', None):
        city = request.GET.get('search_box', None)
        context = {
            'logged': request.user.is_authenticated(),
            'user_name': request.user.username,
            'city': city,
            'category' : category,
            'admin': request.user.is_superuser,
            'restaurants':  Restaurant.objects.filter(city__iexact=city).order_by("category"),
            'promoted': False,
            'viewedrestaurants': _check_session(request)
        }
        return render(request, 'forkilla/restaurants.html', context)
    promoted = False
    if city:
        restaurants_filtered = Restaurant.objects.filter(city__iexact=city).order_by("category")
        if category:
            restaurants_filtered = Restaurant.objects.filter(city__iexact=city).filter(category__iexact=category)
    else:
        restaurants_filtered = Restaurant.objects.filter().order_by("category")
        promoted = False
    viewedrestaurants = _check_session(request)
    context = {
        'city': city,
        'category' : category,
        'restaurants': restaurants_filtered,
        'promoted': promoted,
        'admin': request.user.is_superuser,
        'logged': request.user.is_authenticated(),
        'user_name': request.user.username,
        'viewedrestaurants': viewedrestaurants
    }
    return render(request, 'forkilla/restaurants.html', context)

def details(request,restaurant_number=""):
    try:
        viewedrestaurants = _check_session(request)
        restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
        lastviewed = RestaurantInsertDate(viewedrestaurants=viewedrestaurants, restaurant=restaurant)
        lastviewed.save()
        reviews = Review.objects.filter(restaurant=restaurant)
        context = {
            'logged': request.user.is_authenticated(),
            'user_name': request.user.username,
            'reviews': reviews,
            'city': restaurant.city,
            'category': restaurant.category,
            'admin': request.user.is_superuser,
            'restaurant': restaurant,
            'viewedrestaurants': viewedrestaurants
        }
        return render(request, 'forkilla/details.html', context)

    except Restaurant.DoesNotExist:
        raise Http404


def checkout(request):
    try:
        if request.session["result"]=="OK":
            result = True
            full = False
        elif request.session["result"]=="FULL":
            result = True
            full = True
        viewedrestaurants = _check_session(request)
        context = {
            'logged': request.user.is_authenticated(),
            'user_name': request.user.username,
            'viewedrestaurants': viewedrestaurants,
            'result': result,
            'admin': request.user.is_superuser,
            'full': full,
        }
        return render(request, 'forkilla/checkout.html', context)
    except UnboundLocalError:
        return HttpResponse("No pots reservar per a 0 persones.")

@login_required
def reservation(request):
    try:
        if request.method == "POST":
            form = ReservationForm(request.POST)
            if form.is_valid():
                resv = form.save(commit=False)
                restaurant_number = request.session["reserved_restaurant"]
                resv.restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
                resv.user = request.user
                total_resv = 0
                for reserva in Reservation.objects.filter(restaurant_id=restaurant_number).filter(day=resv.day).filter(time_slot=resv.time_slot):
                    total_resv = total_resv + reserva.num_people
                if total_resv + resv.num_people < resv.restaurant.restaurant_capacity:
                    resv.save()
                    request.session["reservation"] = resv.id
                    request.session["result"] = "OK"
                else:
                    request.session["result"] = "FULL"
            else:
                request.session["result"] = form.errors
            return HttpResponseRedirect(reverse('checkout'))

        elif request.method == "GET":
            restaurant_number = request.GET["reservation"]
            request.session["reserved_restaurant"] = restaurant_number

            form = ReservationForm()
            viewedrestaurants = _check_session(request)
            restaurant = Restaurant.objects.get(restaurant_number = restaurant_number)
            lastviewed = RestaurantInsertDate(viewedrestaurants=viewedrestaurants,restaurant = restaurant)
            lastviewed.save()
            context = {
                'logged': request.user.is_authenticated(),
                'user_name': request.user.username,
                'admin': request.user.is_superuser,
                'restaurant': restaurant,
                'form': form,
                'city': restaurant.city,
                'category': restaurant.category,
                'viewedrestaurants': viewedrestaurants
            }
    except Restaurant.DoesNotExist:
        raise Http404
    return render(request, 'forkilla/reservation.html', context)

@login_required
def reviews(request):
    try:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                revw = form.save(commit=False)
                restaurant_number = request.session["reviewed_restaurant"]
                revw.restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
                revw.user = request.user
                revw.save()
                request.session["reviews"] = revw.id
                request.session["result"] = "OK"
            else:
                request.session["result"] = form.errors
            return HttpResponseRedirect(reverse('restaurants'))

        elif request.method == "GET":
            restaurant_number = request.GET["reviews"]
            request.session["reviewed_restaurant"] = restaurant_number

            form = ReviewForm()
            viewedrestaurants = _check_session(request)
            restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
            context = {
                'logged': request.user.is_authenticated(),
                'user_name': request.user.username,
                'restaurant': restaurant,
                'admin': request.user.is_superuser,
                'form': form,
                'city': restaurant.city,
                'category': restaurant.category,
                'viewedrestaurants': viewedrestaurants
            }
    except Restaurant.DoesNotExist:
        return HttpResponse("Restaurant Does not exists")
    return render(request, 'forkilla/reviews.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })

@login_required
def reservationlist(request):

    if request.method == 'POST':
        Reservation.objects.filter(id = request.POST["delete_reservation"]).delete()
    reservationsPastUser = Reservation.objects.filter(user = request.user).order_by("day").filter(day__range=("2010-01-01", datetime.now().date()-timedelta(1)))
    reservationsFutureUser = Reservation.objects.filter(user = request.user).order_by("day").filter(day__range=(datetime.now().date(), "2020-01-01" ))

    viewedrestaurants = _check_session(request)


    context = {
        'logged': request.user.is_authenticated(),
        'user_name': request.user.username,
        'reviews': reviews,
        'admin': request.user.is_superuser,
        'reservations_past': reservationsPastUser,
        'reservations_future': reservationsFutureUser,
        'viewedrestaurants': viewedrestaurants,

    }

    return render(request, 'forkilla/reservationlist.html', context)

def addrestaurant(request):
    return HttpResponseRedirect(reverse("addrestaurant"))

class RestaurantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Restaurants to be viewed or edited.
    """



    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        queryset = Restaurant.objects.all().order_by('category')

        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category=category)

        city = self.request.query_params.get('city', None)
        if city is not None:
            queryset = queryset.filter(city=city)

        price = self.request.query_params.get('price', None)
        if price is not None:
            queryset = queryset.filter(price_average__lte=price)

        return queryset

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Restaurants to be viewed or edited.
    """
    permission_classes = (IsAdminOrCommercial,)
    queryset = Review.objects.all().order_by('restaurant')
    serializer_class = ReviewSerializer

@login_required
def comparator(request,ips):
    context = {
        'ips' : ips,
        'length' : range(len(ips)) }
    return render(request, 'forkilla/comparator.html', context)