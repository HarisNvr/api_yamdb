import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime

from reviews.models import Category, Genre, Title, User, Review, Comment, \
    GenreTitle


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_PATH
        self.import_categories(os.path.join(csv_path, 'category.csv'))
        self.import_genres(os.path.join(csv_path, 'genre.csv'))
        self.import_users(os.path.join(csv_path, 'users.csv'))
        self.import_titles(os.path.join(csv_path, 'titles.csv'))
        self.import_reviews(os.path.join(csv_path, 'review.csv'))
        self.import_comments(os.path.join(csv_path, 'comments.csv'))
        self.import_genre_titles(os.path.join(csv_path, 'genre_title.csv'))

    def import_categories(self, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Category.objects.update_or_create(
                        id=row['id'],
                        defaults={'name': row['name'], 'slug': row['slug']}
                    )
            self.stdout.write(self.style.SUCCESS('Импортирован category.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка category.csv: {e}'))

    def import_genres(self, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Genre.objects.update_or_create(
                        id=row['id'],
                        defaults={'name': row['name'], 'slug': row['slug']}
                    )
            self.stdout.write(self.style.SUCCESS('Импортирован genre.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка genre.csv: {e}'))

    def import_titles(self, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    category = Category.objects.get(id=row['category'])
                    Title.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'name': row['name'],
                            'category': category
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Импортирован titles.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка titles.csv: {e}'))

    def import_users(self, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    User.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'username': row['username'],
                            'email': row['email'],
                            'role': row['role'],
                            'bio': row.get('bio', ''),
                            'first_name': row.get('first_name', ''),
                            'last_name': row.get('last_name', '')
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Импортирован users.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка users.csv: {e}'))

    def import_reviews(self, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    title = Title.objects.get(id=row['title_id'])
                    author = User.objects.get(id=row['author'])
                    Review.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'title': title,
                            'text': row['text'],
                            'author': author,
                            'score': row['score'],
                            'pub_date': parse_datetime(row['pub_date'])
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Импортирован review.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка review.csv: {e}'))

    def import_comments(self, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    review = Review.objects.get(id=row['review_id'])
                    author = User.objects.get(id=row['author'])
                    Comment.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'review': review,
                            'text': row['text'],
                            'author': author,
                            'pub_date': parse_datetime(row['pub_date'])
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Импортирован comments.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка comments.csv: {e}'))

    def import_genre_titles(self, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    GenreTitle.objects.update_or_create(
                        id=row['id'],
                        defaults={'title': title, 'genre': genre}
                    )
            self.stdout.write(
                self.style.SUCCESS(
                    'Импортирован genre_titles.csv'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка genre_titles.csv: {e}'
                )
            )
