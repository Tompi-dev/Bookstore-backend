from django.urls import path
from .views import generate_books, export_books_csv

urlpatterns = [
    path('books/', generate_books),
    path('books/export/', export_books_csv), 
]
