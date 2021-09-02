from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from .models import Post,Comment
from .forms import EmailPostForm,CommentForm,SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger

from django.contrib.postgres.search import SearchVector

# Create your views here.

class PostListView(ListView):
    queryset=Post.objects.all()
    context_object_name='posts'
    paginate_by=3
    template_name='post_list.html'


def post_list(request, tag_slug=None):
    object_list=Post.objects.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag, slug=tag_slug)
        object_list=object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    
    return render(request, 'post_list.html',{'page': page,'posts': posts,'tag': tag})





def post_detail(request,year,day,month,post):
    post=get_object_or_404(Post,slug=post, status='draft',
    publish__day=day,  publish__month=month, publish__year=year,)
    comments=post.comments.filter(active=True)
    new_comment=None
    if request.method=='POST':
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment=comment_form.save(commit=False)
            new_comment.post=post
            new_comment.save()
    else:
        comment_form=CommentForm()



    return render(request, 'post_detail.html', {'post':post, 'comments':comments,
    'new_comment':new_comment, 'comment_form':comment_form})






def post_share(request, post_id):
    post=get_object_or_404(Post,id=post_id, status='draft')
    sent=False
    if request.method=="POST":
        form=EmailPostForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            post_url=request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'zeratul314@gmail.com',
                      [cd['to']])
            sent=True



    else:
        form=EmailPostForm()
    return render(request, 'post_share.html',{'post':post,'form':form, 'sent':sent})





def post_search(request):
    form=SearchForm()
    query=None
    results=[]
    if 'query' in request.GET:
        form=SearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            results=Post.objects.annotate(search=SearchVector('title','body')).filter(search=query)
    return render(request, 'search.html',{'form': form,
                   'query': query,
                   'results': results})