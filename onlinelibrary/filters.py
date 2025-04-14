
class BookFilterStrategy:
    def filter(self, queryset, query):
        raise NotImplementedError()

class TitleFilter(BookFilterStrategy):
    def filter(self, queryset, query):
        return queryset.filter(title__icontains=query)

class CategoryFilter(BookFilterStrategy):
    def filter(self, queryset, query):
        return queryset.filter(category__icontains=query)

class AuthorFilter(BookFilterStrategy):
    def filter(self, queryset, query):
        return queryset.filter(author__icontains=query)

class PublisherFilter(BookFilterStrategy):
    def filter(self, queryset, query):
        return queryset.filter(publisher__icontains=query)

FILTER_STRATEGIES = {
    "title": TitleFilter(),
    "category": CategoryFilter(),
    "author": AuthorFilter(),
    "publisher": PublisherFilter(),
}
