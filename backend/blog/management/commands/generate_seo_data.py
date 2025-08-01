# backend/blog/management/commands/generate_seo_data.py
from django.core.management.base import BaseCommand
from blog.models import BlogPost
import re

class Command(BaseCommand):
    help = 'Generate SEO data for existing blog posts'
    
    def handle(self, *args, **options):
        posts = BlogPost.objects.filter(meta_description='')
        updated_count = 0
        
        for post in posts:
            # Генерируем meta description из content
            if not post.meta_description and post.content:
                clean_content = re.sub(r'<[^>]+>', '', post.content)
                post.meta_description = clean_content[:160].strip()
                if len(clean_content) > 160:
                    post.meta_description += '...'
            
            # Генерируем meta title из title
            if not post.meta_title and post.title:
                post.meta_title = post.title[:60]
            
            # Генерируем ключевые слова из тегов
            if not post.meta_keywords and post.tags.exists():
                keywords = [tag.name for tag in post.tags.all()]
                post.meta_keywords = ', '.join(keywords[:10])  # Максимум 10 тегов
            
            post.save()
            updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated SEO data for {updated_count} posts')
        )
