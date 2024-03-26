from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, Http404
from django.views.generic import DeleteView, CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy, reverse

from .forms import PostForm, UserEditForm, CommentForm
from .models import Category, Post, Comment

POSTS_AMOUNT: int = 5

User = get_user_model()


def standard_filtration():
    return Post.objects.select_related(
        'category',
        'location'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )

# Старое представление


def index(request):
    template = 'blog/index.html'
    posts = standard_filtration()[:POSTS_AMOUNT]
    context = {'post_list': posts}
    return render(request, template, context)

# Новое представление через CBV


class Index(ListView):
    ordering = '-pub_date'
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related('category', 'location', 'author').annotate(comment_count=Count('comments'))

"""
def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        standard_filtration(),
        pk=post_id
    )
    context = {'post': post}
    return render(request, template, context)
"""


class PostDetailView(DetailView):
    model = Post
    slug_field = 'id'
    slug_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        # При получении объекта не указываем автора.
        # Результат сохраняем в переменную.
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        # Сверяем автора объекта и пользователя из запроса.
        if (
            (not instance.is_published or not instance.category.is_published
             or instance.pub_date > timezone.now())
            and instance.author != request.user
        ):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    posts = standard_filtration().filter(category_id=category.pk)
    context = {'category': category, 'page_obj': posts}
    return render(request, template, context)

class CategoryListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 10

    queryset = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related('category', 'location', 'author').annotate(comment_count=Count('comments'))

    def get_queryset(self):
        return Post.objects.prefetch_related('category', 'location', 'author').filter(
                category__slug=self.kwargs['category_slug'], pub_date__lte=timezone.now(),
        is_published=True, category__is_published=True).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        
        return context

class Profile(ListView):
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.prefetch_related('category', 'location', 'author').filter(
                author__username=self.kwargs['profile']).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            get_user_model(), username=self.kwargs['profile']
        )
        
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user

        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'profile': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    slug_field = 'id'
    slug_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        # При получении объекта не указываем автора.
        # Результат сохраняем в переменную.
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        # Сверяем автора объекта и пользователя из запроса.
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:index')
    slug_field = 'id'
    slug_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'profile'
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'profile': self.kwargs['profile']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    slug_field = 'id'
    slug_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        # При получении объекта не указываем автора.
        # Результат сохраняем в переменную.
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        # Сверяем автора объекта и пользователя из запроса.
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)   

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('blog:index')
    slug_field = 'id'
    slug_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        # При получении объекта не указываем автора.
        # Результат сохраняем в переменную.
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        # Сверяем автора объекта и пользователя из запроса.
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})
