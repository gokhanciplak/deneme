__author__ = 'gokhan'
from django.contrib import admin
from models import UserProfile, Post, Comment




admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Comment)
