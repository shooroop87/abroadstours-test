# backend/blog/feeds.py
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from .models import BlogPost

class BlogFeed(Feed):
    title = "Abroads Tours Blog"
    link = "/blog/"
    description = "Latest travel guides and stories from Abroads Tours"
    
    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.excerpt or item.content[:200] + '...'
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.published_at


class AtomBlogFeed(BlogFeed):
    feed_type = Atom1Feed
    subtitle = BlogFeed.description
