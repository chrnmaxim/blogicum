"""Views of blog app."""
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserEditForm
from .models import Category, Comment, Post

PAGINATOR_ITEMS: int = 10

User = get_user_model()


class PostListMixin(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATOR_ITEMS
    queryset = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related(
        'category', 'location', 'author'
    ).annotate(comment_count=Count('comments'))
    ordering = '-pub_date'


class PostListView(ListView):
    """List view for posts."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATOR_ITEMS
    queryset = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related(
        'category', 'location', 'author'
    ).annotate(comment_count=Count('comments'))
    ordering = '-pub_date'


class Profile(ListView):
    """List view for posts in user profile."""

    template_name = 'blog/profile.html'
    paginate_by = PAGINATOR_ITEMS

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'category', 'location', 'author'
        ).filter(
            author__username=self.kwargs['profile']
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            get_user_model(), username=self.kwargs['profile']
        )

        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for user data update."""

    model = User
    slug_field = 'username'
    slug_url_kwarg = 'profile'
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'profile': self.kwargs['profile']}
        )


class CategoryListView(ListView):
    """List view for posts in a category."""

    template_name = 'blog/category.html'
    paginate_by = PAGINATOR_ITEMS

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'category', 'location', 'author'
        ).filter(
            category__slug=self.kwargs['category_slug'],
            pub_date__lte=timezone.now(),
            is_published=True, category__is_published=True
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )

        return context


class PostDetailView(DetailView):
    """Detail view for a post."""

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


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create view for post creation."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'profile': self.request.user})


class PostUpdateDeleteMixin(LoginRequiredMixin):
    """Mixin for deletion or editing post."""

    model = Post
    form_class = PostForm
    slug_field = 'id'
    slug_url_kwarg = 'post_id'
    template_name = 'blog/create.html'


class PostUpdateView(PostUpdateDeleteMixin, UpdateView):
    """Update view for post update."""

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostUpdateDeleteMixin, DeleteView):
    """Delete view for post deletion."""

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context

    def get_success_url(self):
        return reverse('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Create view for comment creation."""

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
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateDeleteMixin(LoginRequiredMixin):
    """Mixin for deletion or editing a comment."""

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
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(CommentUpdateDeleteMixin, UpdateView):
    """Update view for post update."""

    pass


class CommentDeleteView(CommentUpdateDeleteMixin, DeleteView):
    """Delete view for post update."""

    pass
