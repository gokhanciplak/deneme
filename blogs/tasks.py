__author__ = 'gokhan'
import djcelery
import time
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from celery import task
from django.core.mail import send_mail
from django.template import Context, RequestContext
from django.template.loader import get_template
from models import User, UserProfile, Post
from uuid import uuid4
from datetime import datetime

@task
def send(c_code,email):

    send_mail('Gokhan Ciplak',c_code, 'gkhncplk@gmail.com', [email], fail_silently = False)
    make_link(c_code,email)
    p=datetime.now()
    print p
    print 'c_code'+c_code


def produce_val():
    uid = uuid4()
    return uid.hex


def make_link(c_code,email):
    url = 'http://127.0.0.1:8000/'+c_code+'/confirm'
    send_mail('Gokhan Ciplak',url, 'gkhncplk@gmail.com',
    [email], fail_silently = False)
@task
def send_act_code(act_code,email):
    send_mail('Comment Activation', act_code, 'gkhncplk@gmail.com', [email], fail_silently = False)
    make_link2(act_code,email)

    print 'act_code'+act_code

def make_link2(act_code,email):
    url = 'http://127.0.0.1:8000/'+act_code+'/activate'
    send_mail('Gokhan Ciplak',url, 'gkhncplk@gmail.com',
    [email], fail_silently = False)