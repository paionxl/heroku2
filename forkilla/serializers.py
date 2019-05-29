from .models import Restaurant, Review
from rest_framework import serializers
from django.contrib.auth.models import User

class RestaurantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'restaurant_number', 'name', 'menu_description',
            'price_average', 'is_promot', 'rate', 'address',
            'city', 'country', 'featured_photo', 'category',
            'restaurant_capacity')

class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(many=False, read_only = True)
    user = serializers.PrimaryKeyRelatedField(many=False, read_only = True)
    class Meta:
        model = Review
        fields = (
            'id', 'restaurant', 'user',
            'rating', 'comment'
        )

