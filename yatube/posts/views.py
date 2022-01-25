# post/views
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from users.forms import User
from yatube.settings import SHOW_MAX_POSTS, CACHING_DURATION
from .forms import PostForm, CommentForm
from .models import Post, Group, Follow


def paginator(request, posts):
    paginator_posts = Paginator(posts, SHOW_MAX_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator_posts.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.all()
    page_obj = paginator(request, posts)
    template = 'posts/index.html'
    user = request.user
    context = {'page_obj': page_obj,
               'user': user,
               'CACHING_DURATION': CACHING_DURATION}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.all()
    page_obj = paginator(request, posts)
    user = request.user
    context = {'group': group,
               'page_obj': page_obj,
               'user': user}
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    posts = author.posts.all()
    page_obj = paginator(request, posts)
    template = 'posts/profile.html'
    context = {'author': author,
               'user': user,
               'posts': posts,
               'page_obj': page_obj,
               'following': False,
               'show_subscription': True}

    # Кнопку у себя профайле же видно
    if Follow.objects.filter(author_id=author.id, user_id=user.id):
        context['following'] = True
    if author == user:
        context['show_subscription'] = False
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    count_posts = post.author.posts.count()
    template = 'posts/post_detail.html'
    form = CommentForm(request.POST or None,
                       files=request.FILES or None)
    comments = post.comments.all()
    context = {'post': post, 'count_posts': count_posts, 'form': form,
               'comments': comments}
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    if post.author != user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    template = 'posts/create_post.html'
    context = {'is_edit': True, 'form': form, 'post_id': post_id}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followers = Follow.objects.filter(user_id=request.user.id)
    all_posts = []
    for get_posts in followers:
        all_posts.extend(Post.objects.filter(author=get_posts.author))
    page_obj = paginator(request, all_posts)
    user = request.user
    template = 'posts/follow.html'
    context = {'page_obj': page_obj, 'user': user, }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user.is_authenticated and author != user:
        if not Follow.objects.filter(
                author_id=author.id,
                user_id=user.id).exists():
            Follow.objects.create(author=author, user=user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = Follow.objects.filter(author_id=author.id,
                                   user_id=user.id)
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', username=username)
