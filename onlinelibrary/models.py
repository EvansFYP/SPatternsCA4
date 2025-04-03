from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission

class UserProfile(AbstractUser):  #
    address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="user_profiles", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_profiles", blank=True)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=400)
    publisher = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    isbn_number = models.CharField(max_length=13, unique=True)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return self.title


class BookTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("purchase", "Purchase"),
        ("borrow", "Borrow"),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="transactions")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True) 
    price_at_transaction = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 







    
