__author__ = 'gokhan'
import djcelery
import time
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from celery.task import task
from django.core.mail import send_mail
from django.template import Context, RequestContext
from django.template.loader import get_template
from uuid import uuid4
from datetime import datetime
import PIL
from django.contrib.sites.models import Site
from settings import MEDIA_URL

@task
def send(c_code, email):
    send_mail('Gokhan Ciplak', c_code,
              'gkhncplk@gmail.com',
              [email],
              fail_silently=False)
    make_link(c_code, email)


def produce_val():
    uid = uuid4()
    return uid.hex


def make_link(c_code, email):
    url = str(Site.objects.get_current()) +'/confirm/' + c_code
    send_mail('Gokhan Ciplak', url, 'gkhncplk@gmail.com',
              [email], fail_silently=False)


@task
def send_act_code(act_code, email):
    send_mail('Comment Activation', act_code,
              'gkhncplk@gmail.com', [email],
              fail_silently=False)
    make_link2(act_code, email)


def make_link2(act_code, email):
    url = str(Site.objects.get_current())+'/activate/' + act_code
    send_mail('Gokhan Ciplak', url, 'gkhncplk@gmail.com',
              [email], fail_silently=False)


@task
def resize_image(image):
    """

    :param image:
    """
    import PIL
    from PIL import Image

    basewidth = 200
    img = Image.open( str(Site.objects.get(id=2))+MEDIA_URL + str(image))
    new_image = img
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    new_image = new_image.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    new_image.save(str(Site.objects.get(id=2))+ MEDIA_URL + str(image))
