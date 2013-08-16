from django.contrib.contenttypes import generic
from django.db import models
from django.contrib.auth.models import User, ContentType
import Image
from ckeditor.fields import RichTextField
from django.utils.datetime_safe import datetime


class UserProfile(models.Model):

    user = models.ForeignKey(User)
    image= models.ImageField(null=True, upload_to="images")
    confcode=models.CharField(max_length=100)
    expdate=models.DateField()

class Category(models.Model):

    name = models.CharField(u"Category",max_length = 255)
    slug = models.SlugField(u"Slug")



class Contact(models.Model):
    name = models.CharField(u"Head", max_length=255)
    mail = models.EmailField(u"E-Mail")
    date = models.DateTimeField(u"Date", default=datetime.now())
    message = models.TextField(u"message")

class Comment(models.Model):
    email = models.EmailField(u"E-Mail")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    text = models.CharField(max_length=300)
    is_active = models.NullBooleanField()
    pubdate = models.DateTimeField(u"Date", default=datetime.now())


class Post(models.Model):
    userid = models.ForeignKey(User)
    title = models.CharField(u"Head", max_length = 255)
    slug = models.SlugField(u"Slug")
    keywords = models.CharField(u"Keywords", max_length = 255)
    date = models.DateField(u"Date")
    description = models.TextField(u"Description")
    image = models.ImageField(u"Image", upload_to="images")
    text = RichTextField(u"Text")
    categories = models.ManyToManyField(Category, blank=True, null=True)
    item = generic.GenericRelation(Comment)

    def __unicode__(self):
            return self.title

class Activation(models.Model):
    comment=models.ForeignKey(Comment)
    conf_code=models.CharField(max_length=100)
    exp_date=models.DateField()