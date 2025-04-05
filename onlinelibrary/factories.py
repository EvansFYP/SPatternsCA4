from .models import UserProfile, Book, BookTransaction 


class BookFactory:
    @staticmethod
    def create_book(data, image=None):
        return Book.objects.create(
            title=data.get("title"),
            author=data.get("author"),
            publisher=data.get("publisher"),
            category=data.get("category"),
            price=data.get("price"),
            isbn_number=data.get("isbn_number"),
            stock_quantity=data.get("stock_quantity"),
            image=image,
        )