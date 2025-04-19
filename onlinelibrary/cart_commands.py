from abc import ABC, abstractmethod

class CartCommand(ABC):
    @abstractmethod
    def execute(self): # this is the cart command interface
        pass


#concrete methods 
class AddToCartCommand(CartCommand):
    def __init__(self, cart_service, user, book):
        self.cart_service = cart_service
        self.user = user
        self.book = book
        self.used_free_book = False  # track if we used the free book

    def execute(self):
        if getattr(self.user, "free_book", False):
            price = 0
            self.used_free_book = True
        else:
            price = self.book.price

        self.cart_service.add_to_cart(self.user, self.book, price)

        if self.used_free_book:
            self.user.free_book = False
            self.user.save()

    def undo(self):
        removed = self.cart_service.remove_one_from_cart(self.user, self.book)
        if removed and self.used_free_book:
            # restore the free book if it was used
            self.user.free_book = True
            self.user.save()


class RemoveFromCartCommand(CartCommand):
    def __init__(self, cart_service, user, cart_item_id):
        self.cart_service = cart_service
        self.user = user
        self.cart_item_id = cart_item_id

    def execute(self):
        return self.cart_service.remove_from_cart(self.user, self.cart_item_id)

 

class ClearCartCommand(CartCommand):
    def __init__(self, cart_service, user):
        self.cart_service = cart_service
        self.user = user

    def execute(self):
        self.cart_service.clear_cart(self.user)




