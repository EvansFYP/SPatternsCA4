from django.contrib import admin
from .models import UserProfile, Book, BookTransaction 
from .models import BookComment

admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(BookTransaction)
admin.site.register(BookComment)
