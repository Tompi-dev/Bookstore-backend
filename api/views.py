from rest_framework.decorators import api_view
from rest_framework.response import Response
from faker import Faker
import random
import csv
from django.http import HttpResponse
from rest_framework.decorators import api_view
from faker import Faker
import random
from io import StringIO


def generate_book(seed, lang):
    rng = random.Random(seed)
    faker = Faker(lang)
    faker.seed_instance(seed)

    title = faker.sentence(nb_words=3).rstrip('.')
    authors = [faker.name() for _ in range(rng.choice([1, 2]))]
    publisher = faker.company()
    isbn = faker.isbn13()

    return {
        "title": title,
        "authors": authors,
        "publisher": publisher,
        "isbn": isbn
    }


def generate_likes(seed, avg):
    rng = random.Random(seed)
    value = rng.gauss(avg, 2) 
    return max(0, min(10, round(value)))

def generate_reviews(seed, lang, avg):
    rng = random.Random(seed)
    faker = Faker(lang)
    faker.seed_instance(seed)

    count = int(avg)
    if rng.random() < (avg - count):
        count += 1

    reviews = []
    for _ in range(count):
        reviews.append({
            "text": faker.sentence(),
            "author": faker.name(),
            "source": faker.company()
        })
    return reviews





@api_view(['GET'])
def generate_books(request):
    seed = int(request.GET.get('seed', 0))
    lang = request.GET.get('lang', 'en_US')
    page = int(request.GET.get('page', 1))
    likes_avg = float(request.GET.get('likes', 0))
    reviews_avg = float(request.GET.get('reviews', 0))
    
    books = []
    base_seed = seed + page
    book_rng = random.Random(base_seed)

    for i in range(20):
        index = (page - 1) * 20 + i + 1
        book_seed = book_rng.randint(0, 99999999)

        book = generate_book(book_seed, lang)
        likes = generate_likes(book_seed + 1, likes_avg)
        


        reviews = generate_reviews(book_seed + 2, lang, reviews_avg)
       
        r = book_seed % 256
        g = (book_seed // 2) % 256
        b = (book_seed // 3) % 256
        hex_color = f"{r:02x}{g:02x}{b:02x}"

        cover_url = (
                f"https://placehold.co/100x150/{hex_color}/ffffff"
                f"?text={book['title'].replace(' ', '+')}&font=playfair"
            ) 

        books.append({
            "index": index,
            "isbn": book["isbn"],
            "title": book["title"],
            "authors": book["authors"],
            "publisher": book["publisher"],
            "likes": likes,
            "reviews": reviews,
            "cover": cover_url,

        })

    return Response(books)






@api_view(['GET'])
def export_books_csv(request):
    seed = int(request.GET.get('seed', 0))
    lang = request.GET.get('lang', 'en_US')
    likes_avg = float(request.GET.get('likes', 0))
    reviews_avg = float(request.GET.get('reviews', 0))
    pages = int(request.GET.get('pages', 1))  

    faker = Faker(lang)

    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="books_seed{seed}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Index', 'Title', 'ISBN', 'Authors', 'Publisher', 'Likes', 'Reviews'])

    book_index = 1
    for page in range(1, pages + 1):
        base_seed = seed + page
        book_rng = random.Random(base_seed)

        for i in range(20):
            book_seed = book_rng.randint(0, 99999999)
            rng = random.Random(book_seed)
            faker.seed_instance(book_seed)

            title = faker.sentence(nb_words=3).rstrip('.')
            authors = [faker.name() for _ in range(rng.choice([1, 2]))]
            publisher = faker.company()
            isbn = faker.isbn13()

            
            like_rng = random.Random(book_seed + 1)
            value = like_rng.gauss(likes_avg, 2)
            likes = max(0, min(10, round(value)))

          
            review_rng = random.Random(book_seed + 2)
            faker.seed_instance(book_seed + 2)
            count = int(reviews_avg)
            if review_rng.random() < (reviews_avg - count):
                count += 1

            reviews = []
            for _ in range(count):
                review = f"{faker.sentence()} — {faker.name()} ({faker.company()})"
                reviews.append(review)

            writer.writerow([
                book_index,
                title,
                isbn,
                ', '.join(authors),
                publisher,
                likes,
                ' | '.join(reviews)
            ])
            book_index += 1

    return response
