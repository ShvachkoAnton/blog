from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from .models import Post,Comment
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
# Create your views here.

class PostListView(ListView):
    queryset=Post.objects.all()
    context_object_name='posts'
    paginate_by=3
    template_name='post_list.html'

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