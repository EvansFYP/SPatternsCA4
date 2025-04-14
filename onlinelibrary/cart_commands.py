from abc import ABC, abstractmethod

class CartCommand(ABC):
    @abstractmethod
    def execute(self): # this is the cart command interface
        pass


#concrete methods 
class AddToCartCommand(CartCommand):
    def __init__(self, cart_service, user, book, transaction_type="purchase"):
        self.cart_service = cart_service
        self.user = user
        self.book = book
        self.transaction_type = transaction_type

    def execute(self):
        self.cart_service.add_to_cart(self.user, self.book, self.transaction_type)



class RemoveFromCartCommand(CartCommand):
    def __init__(self, cart_service, user, book):
        self.cart_service = cart_service
        self.user = user
        self.book = book

    def execute(self):
        self.cart_service.remove_from_cart(self.user, self.book)



class ClearCartCommand(CartCommand):
    def __init__(self, cart_service, user):
        self.cart_service = cart_service
        self.user = user

    def execute(self):
        self.cart_service.clear_cart(self.user)




