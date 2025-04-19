from datetime import timezone
from decimal import Decimal
import re
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, authenticate

from .observer import LoyaltyObserver, StockObserver, Subject
from .models import AbstractUser, BookComment
from django.contrib.auth.models import User
from .factories import BookFactory  
from .cart_service import CartService
from .cart_service import CartService
from .cart_commands import AddToCartCommand, ClearCartCommand, RemoveFromCartCommand
from .cart_invoker import CartInvoker 
from django.db.models import Q
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth import logout
from django.dispatch import receiver
from django.db.models.signals import post_save
from .filters import FILTER_STRATEGIES
from django.contrib import messages
from .discountandtransaction import BulkPurchaseDiscount, StaffDiscount, VisaPurchaseProcessor, MasterCardPurchaseProcessor
 


from .models import UserProfile, Book, BookTransaction 

  



def signup(request):
    if request.method == "GET":
        return render(request, "onlinelibrary/signup.html", {})

    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        address = request.POST.get("Address") 
        payment_method = request.POST.get("payment_method") 
        email = request.POST.get("email")
        
        if UserProfile.objects.filter(username=username).exists():
            return render(request, "onlinelibrary/signup.html", {"error": "Username already taken."})

       
        user = UserProfile.objects.create_user(
            username=username,
            password=password,  
            address=address,
            payment_method=payment_method,
            email = email
        )  
  
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("onlinelibrary:home")
        else:
            return render(request, "onlinelibrary/signup.html", {"error": "Failed to authenticate."})

def signin(request):
    if request.method == "GET":
        return render(request, "onlinelibrary/signin.html", {})

    else:
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print("Logged in:", user)
            return redirect(reverse("onlinelibrary:home")) 
        else:
            return render(request, "onlinelibrary/signin.html", {"error": "Invalid credentials."})
        
def custom_logout(request):
    
    if request.user:
        cart_service.clear_cart(request.user)

 
    logout(request)

   
    return redirect('onlinelibrary:signin')
 
def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        subject = Subject()
        stock_observer = StockObserver()
        subject.attach(stock_observer)

        # check all books for low stock 
        low_stock_books = Book.objects.filter(stock_quantity__lt=3)
        subject.notify({
            "event": "admin_visited",
            "user": request.user,
            "request": request,
            "low_stock_books": low_stock_books,
        })

    return render(request, "onlinelibrary/home.html")
    



def additem(request):
    if request.method == "GET":
        return render(request, "onlinelibrary/additem.html", {})

    else:
        image = request.FILES.get("image")
        new_book = BookFactory.create_book(request.POST, image) ##simple factory

        return redirect("onlinelibrary:itemdetail", item_id=new_book.id)
        
 
def viewitem(request):
    items = Book.objects.all()  
    context ={'items': items }
    return render(request, 'onlinelibrary/booklist.html',context)


def itemdetail(request, item_id):
    item = get_object_or_404(Book, id=item_id)
    related_books = Book.objects.filter(author=item.author).exclude(id=item.id)[:5]
    comments = item.comments.select_related('user').order_by('-created_at')  

    context = { 
        'item': item,
        'related_books': related_books,
        'comments': comments,
    }

    return render(request, 'onlinelibrary/itemdetail.html', context)


def deleteitem(request, item_id):
    item = get_object_or_404(Book, id=item_id)
    if request.method == 'GET':
        item.delete()
        return redirect('onlinelibrary:viewitem')
    


def edititem(request, item_id):
    item = get_object_or_404(Book, id=item_id)
    
    if request.method == "POST":
        
        
        item.title = request.POST.get("title", item.title)
        item.author = request.POST.get("author", item.author)
        item.publisher = request.POST.get("publisher", item.publisher)
        item.category = request.POST.get("category", item.category)
        item.price = request.POST.get("price", item.price)
        item.isbn_number = request.POST.get("isbn_number", item.isbn_number)
        item.stock_quantity = request.POST.get("stock_quantity", item.stock_quantity)
        
       
        if 'image' in request.FILES:
            item.image = request.FILES['image']
        
        item.save()
        return redirect('onlinelibrary:itemdetail', item_id=item.id)  # redirect to book detail view after edit
    

    categories = [  
        ('FICTION', 'Fiction'),
        ('NONFICTION', 'Non-Fiction'),
        ('SCIENCE', 'Science'),
        ('HISTORY', 'History'),
        ('BIOGRAPHY', 'Biography'),
        ('MYSTERY', 'Mystery'),
        ('FANTASY', 'Fantasy'),
        ('ROMANCE', 'Romance'),
        ('THRILLER', 'Thriller'),
        ('SELFHELP', 'Self-Help'),
        ('COOKING', 'Cooking'),
       
        
       
    ]
    return render(request, 'onlinelibrary/edititem.html', {
        'item': item,
        'categories': categories
    })




cart_service = CartService() # receiver

executed_commands = {}  # TEMPORARY dictionary 

def add_to_cart(request, item_id):
    book = get_object_or_404(Book, id=item_id)
    user = request.user

    add_command = AddToCartCommand(cart_service, user, book)
    invoker = CartInvoker()
    invoker.execute_command(add_command)

    # store the command for rollback (e.g keyed by user ID)
    executed_commands[user.id] = add_command 

    return redirect('onlinelibrary:viewitem')




def clear_cart(request):
    user = request.user  

    clear_command = ClearCartCommand(cart_service, user)

    
    invoker = CartInvoker()  
    invoker.execute_command(clear_command) 

 
    return redirect('onlinelibrary:view_cart') 



def view_cart(request):
    user = request.user
    cart_items = cart_service.get_cart_items(user)

    total_price = Decimal("0.00")
    total_books = 0

    for item in cart_items:
        total_price += item.price_at_transaction * item.quantity
        total_books += item.quantity

    
    discount_strategy = StaffDiscount() if user.is_staff else BulkPurchaseDiscount()
    discount_amount, discount_reason = discount_strategy.calculate(user, total_price, total_books)

    final_price = total_price - discount_amount

    return render(request, 'onlinelibrary/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount_amount,
        'discount_reason': discount_reason,
        'final_price': final_price,
    }) 


def remove_from_cart(request, item_id):
    user = request.user
    cart_item = get_object_or_404(BookTransaction, id=item_id, user=request.user, status="ACTIVE")
    book = cart_item.book

    #  rollback if a free book was used
    last_command = executed_commands.get(user.id)
    if isinstance(last_command, AddToCartCommand) and last_command.book == book:
        last_command.undo()
        del executed_commands[user.id]  # clear it after undoing
    else:
        # fallback: regular remove
        cart_service.remove_from_cart(user, item_id)

    return redirect('onlinelibrary:view_cart')
 
#Strategy Pattern 
def search_books(request):
    query = request.GET.get("query", "")
    field = request.GET.get("field", "title")
    sort = request.GET.get("sort", "title")

    items = Book.objects.all()

    if query and field in FILTER_STRATEGIES:
        strategy = FILTER_STRATEGIES[field]
        items = strategy.filter(items, query)

    items = items.order_by(sort)

    return render(request, "onlinelibrary/booklist.html", {
        "items": items,
    })


def finalise_purchase(request):
    user = request.user

    if request.method == "POST":
        method = (user.payment_method or "").lower()

        # Create processor
        if method == "visa":
            processor = VisaPurchaseProcessor(request)
        elif method == "mastercard":
            processor = MasterCardPurchaseProcessor(request)
        else:
            return render(request, "onlinelibrary/confirmpurchase.html", {
                "user": user,
                "error": f"Unsupported payment method: {method.title()}"
            })

        # Attach observers 
        processor.subject.attach(LoyaltyObserver())
        processor.subject.attach(StockObserver())

        return processor.execute()

    return render(request, "onlinelibrary/confirmpurchase.html", {"user": user})
 


def loyalty_page(request):
    # get user's profile
    user_profile = request.user
    loyalty_progress = list(range(1, 11))
    # check if the user has made 10 purchases
    if user_profile.loyalty_count >= 10:
        free_book_button = True  #show the free book redemption button
    else:
        free_book_button = False  # hide button

    return render(request, 'onlinelibrary/loyalty_page.html', {
        'user_profile': user_profile,
        'free_book_button': free_book_button,
        'loyalty_progress': loyalty_progress,
    })  


def review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text', '').strip()

        if rating:
            book.update_review(rating)

        if review_text:
            BookComment.objects.create(
                book=book,
                user=request.user,
                comment=review_text
            )

        return redirect('onlinelibrary:review', book_id=book.id)

    return render(request, 'onlinelibrary/review.html', {'book': book}) 

def claim_free_book(request):
    user_profile = request.user
    
    if user_profile.loyalty_count >= 10 and not user_profile.free_book:
        user_profile.free_book = True  # marks the free book as claimed
        user_profile.loyalty_count = 0  # Reset loyalty count
        user_profile.save()
        messages.success(request, 'You have successfully claimed your free book!')
    elif user_profile.free_book:
        messages.warning(request, 'You have already claimed your free book.')
    else:
        messages.error(request, 'You need at least 10 purchases to claim a free book.')

    return redirect('onlinelibrary:loyalty_page')
 
def purchase_history(request):
    transactions = BookTransaction.objects.filter(
        user=request.user,
        transaction_type='purchase',
        status='COMPLETED'
    ).order_by('-transaction_date')

    return render(request, 'onlinelibrary/purchase_history.html', {'transactions': transactions})

def admin_user_purchases(request):
    users = UserProfile.objects.all()
    user_purchases = {}

    for user in users:
        purchases = BookTransaction.objects.filter(user=user, status='COMPLETED')
        if purchases.exists():
            user_purchases[user] = purchases

    return render(request, 'onlinelibrary/userhistory.html', {
        'user_purchases': user_purchases,
    }) 

