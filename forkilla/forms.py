from django import forms
from .models import Reservation
from .models import Review
from .models import Restaurant

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["day", "time_slot", "num_people"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

class ComparatorForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ["city", "price_average","category"]