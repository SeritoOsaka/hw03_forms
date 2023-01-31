from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


def page_look(post_list, request):
    paginator = Paginator(post_list, settings.VIEW_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.select_related('author')
    page_obj = page_look(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    posts_count = author.posts.count()
    page_obj = page_look(author_posts, request)
    context = {
        'author': author,
        'posts': author_posts,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), pk = post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('author')
    page_obj = page_look(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@login_required
def post_create(request):
    form = PostForm(data=request.POST)

    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


def post_edit(request, post_id):
    edit = get_object_or_404(Post.objects.select_related(), pk = post_id)
    form = PostForm(request.POST, instance=edit)

    if edit.author != request.user:
        return redirect('posts:post_detail', post_id)

    if request.method != 'POST' or not form.is_valid():
        form = PostForm(instance=edit)
        return render(
            request,
            'posts/post_create.html',
            {
                'form': form,
                'is_edit': edit
            }
        )

    form.save()
    return redirect('posts:post_detail', post_id)
