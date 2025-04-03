from django.contrib import admin
from .models import UserProfile, Book, BookTransaction 

admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(BookTransaction)
