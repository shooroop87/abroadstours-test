from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from .models import BlogPost, Category

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'
    
    def items(self):
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = 'https'
    
    def items(self):
        return Category.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()
