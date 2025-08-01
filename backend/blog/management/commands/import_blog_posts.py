# backend/blog/management/commands/import_blog_posts.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import BlogPost, Category
import json
import os

class Command(BaseCommand):
    help = 'Import blog posts from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file with posts')
    
    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'File {json_file} does not exist')
            )
            return
        
        with open(json_file, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
        
        created_count = 0
        
        for post_data in posts_data:
            # Получаем или создаем автора
            author_username = post_data.get('author', 'admin')
            author, _ = User.objects.get_or_create(
                username=author_username,
                defaults={'email': f'{author_username}@abroadstours.com'}
            )
            
            # Получаем или создаем категорию
            category = None
            if post_data.get('category'):
                category, _ = Category.objects.get_or_create(
                    name=post_data['category']
                )
            
            # Создаем пост
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults={
                    'author': author,
                    'category': category,
                    'title': post_data['title'],
                    'content': post_data['content'],
                    'excerpt': post_data.get('excerpt', ''),
                    'status': post_data.get('status', 'published'),
                    'meta_title': post_data.get('meta_title', ''),
                    'meta_description': post_data.get('meta_description', ''),
                    'meta_keywords': post_data.get('meta_keywords', ''),
                }
            )
            
            if created:
                created_count += 1
                # Добавляем теги
                if post_data.get('tags'):
                    post.tags.add(*post_data['tags'])
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {created_count} posts')
        )
