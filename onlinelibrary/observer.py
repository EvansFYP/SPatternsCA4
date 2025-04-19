from django.contrib import messages

class Observer:
    def update(self, event_data):
        raise NotImplementedError


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def notify(self, event_data):
        for observer in self._observers:
            observer.update(event_data)


class LoyaltyObserver(Observer):
    def update(self, event_data):
        if event_data.get('event') == 'purchase_completed':
            user = event_data['user']
            print(f"LoyaltyObserver triggered for user: {user.username} with event: {event_data['event']}") ##error chcek
            user.loyalty_count += 1
            user.save()



class StockObserver(Observer):
    def update(self, event_data):
        event = event_data.get("event")
        request = event_data.get("request")

        if event == "purchase_completed": # if admin purchases a book and stock is low notify
            print(f"StockObserver triggered for user: {request.user.username} with event: {event}")
            for book in event_data.get("books", []):
                if book.stock_quantity < 10 and request.user.is_staff:
                    messages.warning(request, f"Low stock alert: '{book.title}' is below threshold.")
        
        elif event == "admin_visited": #Observer to notify admin when stock is low on visit
            print(f"Admin {request.user.username} visited the site.")
            for book in event_data.get("low_stock_books", []):
                messages.warning(request, f"Stock low: '{book.title}' has only {book.stock_quantity} left.")