from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission

class UserProfile(AbstractUser):  #
    address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="user_profiles", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_profiles", blank=True)
    loyalty_count = models.IntegerField(default=0)
    free_book = models.BooleanField(default = False)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=400)
    publisher = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    isbn_number = models.CharField(max_length=13, unique=True)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0) 
    review = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)

    def update_review(self, new_rating):
        total_reviews = self.review * self.review_count
        self.review_count += 1
        new_average = (total_reviews + Decimal(new_rating)) / self.review_count
        self.review = new_average
        self.save() 

    def __str__(self):
        return self.title


class BookTransaction(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    TRANSACTION_TYPE_CHOICES = [
        ("purchase", "Purchase"),
        ("borrow", "Borrow"),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="transactions")
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True) 
    price_at_transaction = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")

    def save(self, *args, **kwargs):
        if self.transaction_type == "purchase" and self.status == "COMPLETED":
            
            self.user.loyalty_count += self.quantity
            self.user.save()
        super().save(*args, **kwargs)


class BookComment(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="user_comments")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.book.title}"






    
