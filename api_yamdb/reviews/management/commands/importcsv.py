import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime

from reviews.models import (
    Category,
    Genre,
    Title,
    User,
    Review,
    Comment
)


class Command(BaseCommand):
    models_files = {
        Category: 'category.csv',
        Genre: 'genre.csv',
        Title: 'titles.csv',
        User: 'users.csv',
        Review: 'review.csv',
        Comment: 'comments.csv',
        Title.genre.through: 'genre_title.csv'
    }

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_PATH
        for model, filename in self.models_files.items():
            self.import_data(model, os.path.join(csv_path, filename))

    def import_data(self, model, filename):
        try:
            with open(filename, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if model == Title:
                        category = Category.objects.get(id=row['category'])
                        row['category'] = category
                    elif model == Review or model == Comment:
                        row['author'] = User.objects.get(id=row['author'])
                        row['pub_date'] = parse_datetime(row['pub_date'])
                    elif model == Title.genre.through:
                        title = Title.objects.get(id=row['title_id'])
                        row['title'] = title
                        genre = Genre.objects.get(id=row['genre_id'])
                        row['genre'] = genre
                    model.objects.update_or_create(id=row['id'], defaults=row)
            self.stdout.write(self.style.SUCCESS(f'Импортирован {filename}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка {filename}: {e}'))
