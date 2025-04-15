from django.conf import settings
from .models import BookTransaction  


from .models import BookTransaction
from django.utils import timezone

class CartService:
    _instance = None # singleton

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_cart_items(self, user):
        return BookTransaction.objects.filter(user=user, status='ACTIVE')

    def add_to_cart(self, user, book, transaction_type="purchase"):
     existing = BookTransaction.objects.filter(user=user, book=book, status="ACTIVE").first()
     if existing:
        existing.quantity += 1
        existing.save()
     else:
         BookTransaction.objects.create(
            user=user,
            book=book,
            transaction_type=transaction_type,
            transaction_date=timezone.now(),
            price_at_transaction=book.price,
            status="ACTIVE",
            quantity=1
        )

    def clear_cart(self, user):
        BookTransaction.objects.filter(user=user, status="ACTIVE").delete()





    def remove_from_cart(self, user, cart_item_id):
  
      try:
         cart_item = BookTransaction.objects.get(
             id=cart_item_id,
             user=user,
             status="ACTIVE",
             transaction_type="purchase"
        )
        
         if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
         else:
            cart_item.delete()
            
         return True
      except BookTransaction.DoesNotExist:
         return False