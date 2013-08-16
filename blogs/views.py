from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.views.generic.base import TemplateView
from forms import UserCreationForm, CommentForm, PostForm, LoginForm
from models import User, UserProfile, Post, Comment, Activation
from django.http import Http404
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
from ckeditor.fields import RichTextField
from tasks import send, produce_val,send_act_code
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
def add_person(request):
    success = False

    if request.method == "POST":
        user_form = UserCreationForm(request.POST, request.FILES)

        if user_form.is_valid():
            success = True

            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            username = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password1']
            passwordt = user_form.cleaned_data['password2']
            email = user_form.cleaned_data['email']
            image = user_form.cleaned_data['image']

            try:
                if password != passwordt:
                    error = u'Passwords have to be same'
                    return render_to_response('blog/add_person.html', {'user_form': user_form,
                                                                       'error': error},
                                              context_instance=RequestContext(request))

                new_user = User(first_name=first_name, last_name=last_name, username=email,
                                email=email, is_active=0, is_staff=0, is_superuser=0,
                                date_joined=datetime.now())
                new_user.set_password(password)
                new_user.save()
                ccode=produce_val() #producing confirmation code
                print "burasi view"
                print ccode
                send.delay(ccode,email)
                user = new_user.id
                new_profile = UserProfile(user_id=user, image=image, confcode=ccode, expdate=datetime.now())
                new_profile.save()

                new_user_form = UserCreationForm()

                ctx2 = {'success': success, 'user_form': new_user_form}
                return render_to_response('blog/add_person.html', ctx2, context_instance=RequestContext(request))
            except:
                try:
                    users = User.objects.get(email__iexact=email)
                    error = u'us comments=ername was already taken'
                    return render_to_response('blog/add_person.html', {'user_form': user_form, 'error': error},
                                              context_instance=RequestContext(request))
                except:
                    if password == passwordt:
                        error = u'Database Error'
                        return render_to_response('blog/add_person.html', {'user_form': user_form, 'error': error},
                                                  context_instance=RequestContext(request))

                return render_to_response('blog/add_person.html', {'user_form': user_form, 'error': error},
                                          context_instance=RequestContext(request))


    else:
        user_form = UserCreationForm()
    ctx = {'user_form': user_form}
    return render_to_response('blog/add_person.html', ctx, context_instance=RequestContext(request))


def add_post(request):
    if request.method == "POST":
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            title = post_form.cleaned_data['title']
            keywords = post_form.cleaned_data['keywords']
            description = post_form.cleaned_data['description']
            image = post_form.cleaned_data['image']
            text = post_form.cleaned_data['text']

            try:
            # new_post = Post(title=title, keywords=keywords, date=date, text=text, keywords=keywords,
            # description=description, image=image, slug="slug")
                new_post = Post(title=title, keywords=keywords, image=image, text=text, description=description,
                                date=datetime.now())
                new_post.save()
                post_form = PostForm()
                ctx = {'post_form': post_form}
                return render_to_response('blog/add_post.html', ctx, context_instance=RequestContext(request))
            except:

                user_form = UserCreationForm()
                ctx = {'user_form': user_form}
                return render_to_response('blog/add_person.html', ctx, context_instance=RequestContext(request))
    else:
        post_form = PostForm()
    ctx = {'post_form': post_form}
    return render_to_response('blog/add_post.html', ctx, context_instance=RequestContext(request))


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment=post.item.all()

    comments_of_comment=Comment.objects.filter(content_type_id=10,)



    # for i in range (item.__len__()):
    #     try:
    #         comments_of_comment.append(Comment.objects.get(content_type_id=10, object_id=item[i].id))
    #     except:
    #         pass

    t = get_template('blog/posts.html')
    html = t.render(Context({'post': post, 'post_comments': comment,'cc':comments_of_comment,}, ))
    return HttpResponse(html)

def show_post2(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    comments_of_post=post.item.all()
    id_list = []
    for i in range(comments_of_post.__len__()):
        id_list.append(comments_of_post[i].id)

    my_list = []
    for x in id_list:
        my_list.append(x)

        # print x

    #to get only comments of comments which are made post i am listing on the page
    comments_of_comment=Comment.objects.filter(content_type_id=10 ).filter(object_id__in=my_list).filter(is_active=1)
    if request.method == "POST":

        form = CommentForm(request.POST)
        if form.is_valid():
            text =form.cleaned_data["text"]
            email =form.cleaned_data["email"]
            c_type = request.POST.get("c_type")
            obj_id = request.POST.get("replyfor")
            print email
            if c_type == "Comment":
                    c_model=Comment
            if c_type == "Post":
                    c_model=Post
            con_type = ContentType.objects.get_for_model(c_model)
            new_comment=Comment(email=email, text=text, content_type = con_type, object_id = obj_id,
                                pubdate = datetime.now(), is_active=0)
            new_comment.save()

            if(request.user.is_authenticated()):
                new_comment.is_active=1
                new_comment.save()
            else:
                act_code = produce_val()
                send_act_code(act_code,new_comment.email)
                print act_code
                new_activation= Activation(conf_code = act_code, comment = new_comment,
                                           exp_date=datetime.now(),)
                new_activation.save()
        form = CommentForm()
    else:
        form = CommentForm()
    user = request.user
    return render(request, 'blog/posts.html', {'post': post, 'post_comments': comments_of_post,
            'cc':comments_of_comment,'form': form, 'user': user }, context_instance=RequestContext(request))


def loginn(request):


    def errorHandle(error):
        form = LoginForm()
        return render_to_response('blog/login.html', {
            'error': error,
            'form': form,
        }, context_instance=RequestContext(request))

    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # Redirect to a success page.
                    login(request, user)
                    return render_to_response('blog/logged_in.html', {
                        'username': username,
                    }, context_instance=RequestContext(request))
                else:
                    # Return a 'disabled account' error message

                    error = u'account disabled'
                    return errorHandle(error)
            else:
            # Return an 'invalid login' error message.
                error = u'invalid login'
                return errorHandle(error)
        else:
            error = u'form is invalid'
            return errorHandle(error)
    else:
        form = LoginForm() # An unbound form
        return render_to_response('blog/login.html', {
            'form': form,
        }, context_instance=RequestContext(request))

def confirm(request):

    return render_to_response('blog/confirm.html', {

        }, context_instance=RequestContext(request))


def conf2(request, c_code):
      if confirm_email(c_code):
          msg="Your email is verified"
      else:
          msg="Your email is not verified"
      return render(request, 'blog/conf.html', {
          'ccode':msg, }, context_instance=RequestContext(request))

def activate(request, ccode):
      if confirm_comment(ccode):
          msg="Your comment is activated"
      else:
          msg="Your comment can not be activated"
      return render(request, 'blog/conf.html', {
          'ccode':msg, }, context_instance=RequestContext(request))

def confirm_email(c_code):
        user_pr = get_object_or_404(UserProfile, conf_code=c_code)
        user = get_object_or_404(User, id=user_pr.user_id)
        user.is_active = 1
        user.save()
        return True
def confirm_comment(c_code):
        act = get_object_or_404(Activation, conf_code=c_code)
        comment = get_object_or_404(Comment, id=act.comment.id)
        comment.is_active = 1
        comment.save()
        return True
     # try:
     #    userpr= get_object_or_404(UserProfile, confcode=ccode)
     #    user=get_object_or_404(User,id=userpr.user)
     #    user.is_active=1
     #    user.save()
     #    return True     posts
     # except:
     #    return False

def posts(request):
    posts = Post.objects.order_by('-id')
    t = get_template('blog/allposts.html')
    html = t.render(Context({'posts': posts}))
    return HttpResponse(html)

class EmailOrUsernameModelBackend(object):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None