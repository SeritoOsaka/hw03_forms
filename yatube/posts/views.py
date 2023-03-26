from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


def page_look(post_list, page_number):
    paginator = Paginator(post_list, settings.VIEW_COUNT)
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_number = request.GET.get('page')
    page_obj = page_look(post_list, page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.select_related('group')
    page_number = request.GET.get('page')
    page_obj = page_look(author_posts, page_number)
    context = {
        'author': author,
        'author_posts': author_posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author__exact=post.author).count
    context = {
        "post": post,
        "posts_count": posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_number = request.GET.get('page')
    page_obj = page_look(post_list, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post_create = form.save(commit=False)
        post_create.author = request.user
        post_create.save()
        return redirect('posts:profile', post_create.author)
    template = 'posts/post_create.html'
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)
    if form.is_valid():
        post = form.save()
        form.instance.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, "posts/post_create.html", context)
