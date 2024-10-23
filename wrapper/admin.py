from django.contrib import admin

from .models import Admin, FoodLocation, Review, UserProfile

admin.site.register(UserProfile)
admin.site.register(Admin)
admin.site.register(Review)
admin.site.register(FoodLocation)
