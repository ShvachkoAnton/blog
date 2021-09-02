from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Post
class LatestPostFeed(Feed):
    title='Мой блог'
    link=reverse_lazy('post_list')
    description='Новые посты моего блога'
    def items(self):
        return Post.objects.all()[:5]
    def item_title(self,item):
        return item.title
    def item_description(self,item):
        return truncatewords(item.body, 30)