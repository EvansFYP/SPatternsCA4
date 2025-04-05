from django.conf import settings
from .models import BookTransaction  


from .models import BookTransaction
from django.utils import timezone

class CartService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_cart_items(self, user):
        return BookTransaction.objects.filter(user=user, status='ACTIVE')

    def add_to_cart(self, user, book, transaction_type="purchase"): # assume book is purchased for now
        #if book exists dont add it again
        existing = BookTransaction.objects.filter(user=user, book=book, status="ACTIVE").first()
        if not existing:
            BookTransaction.objects.create(
                user=user,
                book=book,
                transaction_type=transaction_type,
                transaction_date=timezone.now(),
                price_at_transaction=book.price,
                status="ACTIVE"
            )

    def clear_cart(self, user):
        BookTransaction.objects.filter(user=user, status="ACTIVE").delete()


## REMOVE ITEM FROM CART METHOD NEXT 