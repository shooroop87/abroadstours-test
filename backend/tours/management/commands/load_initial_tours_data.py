# backend/tours/management/__init__.py
# Пустой файл

# backend/tours/management/commands/__init__.py  
# Пустой файл

# backend/tours/management/commands/load_initial_tours_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from tours.models import TourCategory, TourDifficulty


class Command(BaseCommand):
    help = 'Load initial data for Tours app (categories and difficulty levels)'
    
    def handle(self, *args, **options):
        self.stdout.write('🎯 Loading initial Tours data...')
        
        with transaction.atomic():
            # Создаем категории туров
            self.create_tour_categories()
            # Создаем уровни сложности
            self.create_difficulty_levels()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Successfully loaded initial Tours data!')
        )
    
    def create_tour_categories(self):
        """Создаем основные категории туров"""
        categories_data = [
            {
                'name_en': 'Wine Tours',
                'slug_en': 'wine-tours', 
                'description_en': 'Discover the finest wines and vineyards of Italy',
                'icon': 'icon-wine',
                'sort_order': 1
            },
            {
                'name_en': 'Lake Como Tours',
                'slug_en': 'lake-como-tours',
                'description_en': 'Explore the stunning beauty of Lake Como and surrounding areas',
                'icon': 'icon-lake',
                'sort_order': 2
            },
            {
                'name_en': 'City Tours',
                'slug_en': 'city-tours',
                'description_en': 'Urban exploration and cultural experiences in Italian cities',
                'icon': 'icon-city',
                'sort_order': 3
            },
            {
                'name_en': 'Nature Tours',
                'slug_en': 'nature-tours',
                'description_en': 'Immerse yourself in the natural beauty of Italy',
                'icon': 'icon-mountain',
                'sort_order': 4
            },
            {
                'name_en': 'Cultural Tours',
                'slug_en': 'cultural-tours',
                'description_en': 'Deep dive into Italian history, art, and traditions',
                'icon': 'icon-culture',
                'sort_order': 5
            },
            {
                'name_en': 'Food Tours',
                'slug_en': 'food-tours',
                'description_en': 'Culinary adventures and authentic Italian cuisine experiences',
                'icon': 'icon-food',
                'sort_order': 6
            }
        ]
        
        for cat_data in categories_data:
            category, created = TourCategory.objects.get_or_create(
                translations__slug=cat_data['slug_en'],
                defaults={
                    'icon': cat_data['icon'],
                    'sort_order': cat_data['sort_order'],
                    'is_active': True
                }
            )
            
            if created:
                # Устанавливаем переводы
                category.set_current_language('en')
                category.name = cat_data['name_en']
                category.slug = cat_data['slug_en'] 
                category.description = cat_data['description_en']
                category.save()
                
                self.stdout.write(f'✅ Created category: {cat_data["name_en"]}')
            else:
                self.stdout.write(f'ℹ️  Category already exists: {cat_data["name_en"]}')
    
    def create_difficulty_levels(self):
        """Создаем уровни сложности"""
        difficulty_data = [
            {
                'name': 'Easy',
                'level': 1,
                'icon': 'icon-easy',
                'color': '#46b450'
            },
            {
                'name': 'Moderate', 
                'level': 2,
                'icon': 'icon-moderate',
                'color': '#0073aa'
            },
            {
                'name': 'Challenging',
                'level': 3,
                'icon': 'icon-challenging', 
                'color': '#f56e28'
            },
            {
                'name': 'Difficult',
                'level': 4,
                'icon': 'icon-difficult',
                'color': '#dc3232'
            },
            {
                'name': 'Expert',
                'level': 5,
                'icon': 'icon-expert',
                'color': '#826eb4'
            }
        ]
        
        for diff_data in difficulty_data:
            difficulty, created = TourDifficulty.objects.get_or_create(
                name=diff_data['name'],
                defaults={
                    'level': diff_data['level'],
                    'icon': diff_data['icon'],
                    'color': diff_data['color']
                }
            )
            
            if created:
                self.stdout.write(f'✅ Created difficulty level: {diff_data["name"]} (Level {diff_data["level"]})')
            else:
                self.stdout.write(f'ℹ️  Difficulty level already exists: {diff_data["name"]}')
        
        self.stdout.write('🎯 Tour categories and difficulty levels loaded successfully!')


# Команда для загрузки данных:
# python manage.py load_initial_tours_data