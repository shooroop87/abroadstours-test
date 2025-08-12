# backend/blog/management/commands/create_test_posts.py
import os
import requests
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.base import ContentFile
from blog.models import BlogPost, Category

class Command(BaseCommand):
    help = 'Создает тестовые посты с изображениями для отладки'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== СОЗДАНИЕ ТЕСТОВЫХ ПОСТОВ ==="))
        
        # Создаем автора если не существует
        author, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            author.set_password('admin123')
            author.save()
            self.stdout.write(f"✅ Создан пользователь: {author.username}")
        else:
            self.stdout.write(f"ℹ️ Пользователь уже существует: {author.username}")
        
        # Создаем категорию
        category, created = Category.objects.get_or_create(
            defaults={'is_active': True}
        )
        
        if created or not category.safe_translation_getter('name'):
            category.name = 'Travel Guide'
            category.slug = 'travel-guide'
            category.description = 'Travel guides and tips'
            category.save()
            self.stdout.write(f"✅ Создана категория: {category.name}")
        
        # Создаем директории для медиа
        media_dirs = [
            Path(settings.MEDIA_ROOT) / 'blog',
            Path(settings.MEDIA_ROOT) / 'blog' / 'featured',
            Path(settings.MEDIA_ROOT) / 'blog' / 'images',
        ]
        
        for dir_path in media_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f"📁 Создана директория: {dir_path}")
        
        # Создаем тестовые посты
        test_posts = [
            {
                'title': 'Lake Como Ultimate Guide',
                'slug': 'lake-como-ultimate-guide',
                'content': '''<h2>Discover Lake Como</h2>
                <p>Lake Como is one of Italy's most beautiful destinations. This comprehensive guide covers everything you need to know.</p>
                <h3>Best Time to Visit</h3>
                <p>The best time to visit Lake Como is from April to October when the weather is pleasant and boats are running regularly.</p>''',
                'excerpt': 'Complete guide to visiting Lake Como - from best viewpoints to hidden gems.',
                'image_url': 'https://picsum.photos/1200/630?random=1',
            },
            {
                'title': 'Barolo Wine Region Tours',
                'slug': 'barolo-wine-region-tours',
                'content': '''<h2>Wine Tasting in Barolo</h2>
                <p>Explore the prestigious Barolo wine region in Piedmont, known for producing some of Italy's finest wines.</p>
                <h3>What to Expect</h3>
                <p>Professional wine tastings, scenic vineyard walks, and authentic Italian cuisine.</p>''',
                'excerpt': 'Discover the world-famous Barolo wine region with our expert guides.',
                'image_url': 'https://picsum.photos/1200/630?random=2',
            },
            {
                'title': 'Milan Hidden Gems Walking Tour',
                'slug': 'milan-hidden-gems-walking-tour',
                'content': '''<h2>Explore Milan Like a Local</h2>
                <p>Beyond the Duomo and La Scala, Milan has many hidden treasures waiting to be discovered.</p>
                <h3>Secret Spots</h3>
                <p>We'll show you courtyards, galleries, and local markets that tourists rarely see.</p>''',
                'excerpt': 'Discover Milan\'s best-kept secrets on this exclusive walking tour.',
                'image_url': 'https://picsum.photos/1200/630?random=3',
            }
        ]
        
        for post_data in test_posts:
            # Проверяем, существует ли пост
            if BlogPost.objects.filter(translations__slug=post_data['slug']).exists():
                self.stdout.write(f"⚠️ Пост уже существует: {post_data['slug']}")
                continue
            
            # Создаем пост
            post = BlogPost.objects.create(
                author=author,
                category=category,
                status='published',
                is_featured=True,
                allow_comments=True,
            )
            
            # Устанавливаем переводимые поля
            post.title = post_data['title']
            post.slug = post_data['slug']
            post.content = post_data['content']
            post.excerpt = post_data['excerpt']
            post.save()
            
            # Загружаем и сохраняем изображение
            try:
                response = requests.get(post_data['image_url'], timeout=10)
                if response.status_code == 200:
                    image_content = ContentFile(response.content)
                    image_name = f"{post_data['slug']}.jpg"
                    post.featured_image.save(image_name, image_content, save=True)
                    self.stdout.write(f"✅ Создан пост с изображением: {post.get_display_title()}")
                else:
                    self.stdout.write(f"❌ Ошибка загрузки изображения для: {post_data['title']}")
            except requests.exceptions.RequestException as e:
                self.stdout.write(f"❌ Ошибка сети при загрузке изображения: {e}")
                # Создаем пост без изображения
                self.stdout.write(f"⚠️ Создан пост без изображения: {post.get_display_title()}")
        
        self.stdout.write(self.style.SUCCESS("=== СОЗДАНИЕ ТЕСТОВЫХ ПОСТОВ ЗАВЕРШЕНО ==="))
        
        # Показываем статистику
        total_posts = BlogPost.objects.count()
        posts_with_images = BlogPost.objects.exclude(featured_image='').count()
        
        self.stdout.write(f"📊 Всего постов: {total_posts}")
        self.stdout.write(f"📊 Постов с изображениями: {posts_with_images}")
        
        # Проверяем медиа-директории
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists():
            blog_images = list((media_root / 'blog' / 'featured').glob('*.jpg'))
            self.stdout.write(f"📊 Изображений в media/blog/featured/: {len(blog_images)}")
            for img in blog_images:
                size = img.stat().st_size
                self.stdout.write(f"  - {img.name} ({size} bytes)")
        
        self.stdout.write(self.style.SUCCESS("🎉 ВСЕ ГОТОВО!"))
        self.stdout.write("Теперь перейдите на /blog/ чтобы увидеть результат.")
