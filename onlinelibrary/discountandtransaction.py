import re
from abc import ABC, abstractmethod # abstract base class
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect
from onlinelibrary.models import BookTransaction


#strategy pattern for discounts
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, user, total_price: Decimal, total_books: int) -> tuple[Decimal, str]:
        pass


class NoDiscount(DiscountStrategy):
    def calculate(self, user, total_price, total_books):
        return Decimal("0.00"), ""


class StaffDiscount(DiscountStrategy):
    def calculate(self, user, total_price, total_books):
        if user.is_staff:
            amount = (total_price * Decimal("0.20")).quantize(Decimal("0.01"))
            return amount, "Staff Discount (20%)"
        return Decimal("0.00"), ""


class BulkPurchaseDiscount(DiscountStrategy):
    def calculate(self, user, total_price, total_books):
        if total_books >= 3:
            amount = (total_price * Decimal("0.15")).quantize(Decimal("0.01"))
            return amount, "Bulk Purchase Discount (15%)"
        return Decimal("0.00"), ""
    

    #templatepattern
class PurchaseProcessor(ABC):
    def __init__(self, request, discount_strategy: DiscountStrategy = None):
        self.request = request
        self.user = request.user
        self.card_number = request.POST.get("card_number", "").replace(" ", "")
        self.context = {"user": self.user}
        self.discount_strategy = discount_strategy or NoDiscount()

    def execute(self):
        if not self.validate_payment():
            return self.handle_invalid_payment()

        if not self.process_transactions():
            return redirect("onlinelibrary:view_cart")

        return self.finalise()

    @abstractmethod
    def validate_payment(self) -> bool:
        pass

    @abstractmethod
    def handle_invalid_payment(self):
        pass

    def process_transactions(self):
        active_transactions = BookTransaction.objects.select_related("book").filter(
            user=self.user, status="ACTIVE"
        )

        for trans in active_transactions:
            book = trans.book
            if book.stock_quantity >= trans.quantity:
                book.stock_quantity -= trans.quantity
                book.save()

                trans.status = "COMPLETED"
                trans.save()
            else:
                print(f"Not enough stock for '{book.title}'. Purchase canceled.")
                return False

        return True

    def finalise(self):
        messages.success(self.request, "Purchase processed successfully. Thank you!")
        return redirect("onlinelibrary:submit_review")

    def apply_discount(self, total_price, total_books):
        return self.discount_strategy.calculate(self.user, total_price, total_books)


class VisaPurchaseProcessor(PurchaseProcessor):
    def validate_payment(self) -> bool:
        return bool(re.fullmatch(r"^4[0-9]{12}(?:[0-9]{3})?$", self.card_number))

    def handle_invalid_payment(self):
        self.context["error"] = "Invalid Visa card number."
        return render(self.request, "onlinelibrary/confirmpurchase.html", self.context)

class MasterCardPurchaseProcessor(PurchaseProcessor):
    def validate_payment(self) -> bool:
        return bool(re.fullmatch(r"^5[1-5][0-9]{14}$", self.card_number))

    def handle_invalid_payment(self):
        self.context["error"] = "Invalid MasterCard number."
        return render(self.request, "onlinelibrary/confirmpurchase.html", self.context)
    


