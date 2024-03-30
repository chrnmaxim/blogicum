"""Module of blog app admin panel."""
from django.contrib import admin

from .models import Category, Comment, Location, Post, Profanity

admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Profanity)
