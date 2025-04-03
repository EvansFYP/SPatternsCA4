from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, authenticate
from .models import AbstractUser
from django.contrib.auth.models import User

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

def home(request): 
    if request.method == "GET":
        
          
        context = {}
        return render(request, "onlinelibrary/home.html", context)
    else:
     
         return HttpResponseRedirect(reverse("onlinelibrary:home"))
    

def additem(request):
    if request.method == "GET":
        context = {} 
        return render(request, "onlinelibrary/additem.html", context)
    else:
        title = request.POST["title"]
        author = request.POST["author"]
        publisher = request.POST["publisher"]
        category = request.POST["category"]
        price = request.POST["price"]
        isbn_number = request.POST["isbn_number"]
        stock_quantity = request.POST["stock_quantity"]
        image = request.FILES.get("image", None)


        ## Create Book object
        new_book = Book.objects.create(
           
            category=category,
            title=title,
            author=author,
            publisher=publisher,
            price=price,
            isbn_number=isbn_number,
            stock_quantity=stock_quantity,
            image=image,
        )

    
        return HttpResponseRedirect(reverse("webapp:viewitem", kwargs={"item_id": new_book.id}))
        
 
def viewitem(request):
    items = Book.objects.all()  
    context ={'items': items }
    return render(request, 'onlinelibrary/viewitem.html',context)


def itemdetail(request, item_id):
    item = get_object_or_404(Book, id=item_id)

    context = { 
        'item': item,
    }
    
    
    return render(request, 'onlinelibrary/bookdetail.html', context)


def deleteitem(request, item_id):
    item = get_object_or_404(Book, id=item_id)
    if request.method == 'GET':
        item.delete()
        return redirect('onlinelibrary:viewitem')

def edititem(request, item_id):
    item = get_object_or_404(Book, id=item_id)
    

    if request.method == "POST":
       
       item.title = request.POST["title"]
       item.author = request.POST["author"]
       item.publisher = request.POST["publisher"]
       item.category = request.POST["category"]
       item.price = request.POST["price"]
       item.isbn_number = request.POST["isbn_number"]
       item.stock_quantity = request.POST["stock_quantity"]
       item.image = request.FILES.get("image", item.image)  

        
        
       item.save()

      
    return redirect('webapp:viewitem')