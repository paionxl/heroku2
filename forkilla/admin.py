from django.contrib import admin
from .models import Restaurant
from .models import Review
from .models import Reservation

admin.site.register(Restaurant)
admin.site.register(Review)
admin.site.register(Reservation)
