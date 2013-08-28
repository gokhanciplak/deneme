__author__ = 'gokhan'
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Form
from models import Post, Comment
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextField
attrs_dict = {'class': 'required'}


class UserCreationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u'email address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_(u'password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_(u'password (again)'))
    first_name = forms.CharField(max_length=100)

    last_name = forms.CharField(max_length=100)

    image = forms.ImageField(required=False)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'categories', 'keywords', 'image', 'description' )


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False),
                               max_length=100)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('email', 'text')
        text = forms.CharField(max_length=100)

        # content = forms.CharField(max_length=100)