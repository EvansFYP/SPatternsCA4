from datetime import timezone
from decimal import Decimal
import re
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, authenticate
from .models import AbstractUser
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

   
    return redirect('onlinelibrary:home')
 
def home(request): 
    if request.method == "GET":
        
          
        context = {}
        return render(request, "onlinelibrary/home.html", context)
    else:
     
         return HttpResponseRedirect(reverse("onlinelibrary:home"))
    



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

    context = { 
        'item': item,
        'related_books': related_books,
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
        return redirect('onlinelibrary:itemdetail', item_id=item.id)  # Redirect to detail view after edit
    

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




cart_service = CartService()

def add_to_cart(request, item_id):
    book = get_object_or_404(Book, id=item_id)
    user = request.user  
    # create the AddToCartCommand
    add_command = AddToCartCommand(cart_service, user, book)

    # create an Invoker and execute the command
    invoker = CartInvoker()  
    invoker.execute_command(add_command)  # executes the command through the invoker

 
    return redirect('onlinelibrary:view_cart')




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

    # Default discount logic
    discount = Decimal("0.00")
    discount_reason = ""

    if user.is_staff:
        discount = Decimal("0.20")
        discount_reason = "Staff Discount (20%)"
    elif total_books >= 3:
        discount = Decimal("0.15")
        discount_reason = "Bulk Purchase Discount (3+ books - 15%)"

    discount_amount = (total_price * discount).quantize(Decimal("0.01"))
    final_price = total_price - discount_amount

    return render(request, 'onlinelibrary/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount_amount,
        'discount_reason': discount_reason,
        'final_price': final_price,
    })

 


def remove_from_cart(request, item_id):
    remove_command = RemoveFromCartCommand(cart_service, request.user, item_id)
    invoker = CartInvoker()
    invoker.execute_command(remove_command)
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
        card_number = request.POST.get("card_number", "").replace(" ", "")
        method = (user.payment_method or "").lower()

        visa_regex = re.compile(r"^4[0-9]{12}(?:[0-9]{3})?$")
        master_regex = re.compile(r"^5[1-5][0-9]{14}$")

        is_valid = False
        if method == "visa":
            is_valid = bool(visa_regex.fullmatch(card_number))
        elif method == "mastercard":
            is_valid = bool(master_regex.fullmatch(card_number))

        if not is_valid:
            return render(request, "onlinelibrary/confirmpurchase.html", {
                "error": f"Invalid {method.title()} card number.",
                "user": user
            })

        # Proceed with purchase
        active_transactions = BookTransaction.objects.select_related('book').filter(
            user=user, status="ACTIVE"
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
                return redirect('onlinelibrary:view_cart')

        # 
        messages.success(request, "Purchase processed successfully. Thank you!")

        return redirect('onlinelibrary:submit_review')

    return render(request, 'onlinelibrary/confirmpurchase.html', {"user": user})



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


def submit_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')

        #update the book's average review rating
        book.update_review(rating)

      
        return redirect('itemdetail', book_id=book.id)  

def purchase_history(request):
    transactions = BookTransaction.objects.filter(
        user=request.user,
        transaction_type='purchase',
        status='COMPLETED'
    ).order_by('-transaction_date')

    return render(request, 'onlinelibrary/purchase_history.html', {'transactions': transactions})
