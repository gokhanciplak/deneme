from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template.defaulttags import register
from django.template.loader import get_template
from django.template import Context, RequestContext
from forms import UserCreationForm, CommentForm, PostForm, LoginForm
from models import User, UserProfile, Post, Comment, Activation
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from blog.tasks import send, produce_val, send_act_code, resize_image
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.core.validators import email_re
from django.utils.translation import ugettext
from django.contrib import messages
from django.contrib.auth import logout


def add_person(request):
    """

    :param request:
    :return:
    """
    if request.method == "POST":
        user_form = UserCreationForm(request.POST, request.FILES)
        if user_form.is_valid():
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            username = produce_val()
            password = user_form.cleaned_data['password1']
            password_t = user_form.cleaned_data['password2']
            email = user_form.cleaned_data['email']
            image = user_form.cleaned_data['image']
            if password != password_t:
                error = ugettext('Passwords have to be same')
                return render_to_response('blog/add_person.html',
                                          {'user_form': user_form,
                                           'error': error},
                                          context_instance=RequestContext(request))

            if email_check(email) == 0:
                error = ugettext('This e-mail was already in use')
                return render_to_response('blog/add_person.html', {'user_form': user_form, 'error': error},
                                          context_instance=RequestContext(request))
            else:
                new_user = User(first_name=first_name,
                                last_name=last_name,
                                username=username,
                                email=email,
                                is_active=0,
                                is_staff=0,
                                is_superuser=0,
                                date_joined=datetime.now())
                new_user.set_password(password)
                new_user.save()
                #producing confirmation code
                c_code = produce_val()
                send.delay(c_code, email)
                user = new_user.id
                new_profile = UserProfile(user_id=user,
                                          image=image,
                                          conf_code=c_code,
                                          exp_date=datetime.now())
                new_profile.save()
                return HttpResponseRedirect('/login/')
    else:
        user_form = UserCreationForm()
    return render(request,
                  'blog/add_person.html',
                  {'user_form': user_form}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def add_post(request):
    if request.method == "POST":
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            title = post_form.cleaned_data['title']
            keywords = post_form.cleaned_data['keywords']
            description = post_form.cleaned_data['description']
            image = post_form.cleaned_data['image']
            text = post_form.cleaned_data['text']
            slug = title
            try:
                new_post = Post(title=title,
                                userid=request.user,
                                slug=slug,
                                keywords=keywords,
                                image=image,
                                text=text,
                                description=description,
                                date=datetime.now())
                new_post.save()
                post_form = PostForm()
                return render(request,
                              'blog/add_post.html',
                              {'post_form': post_form},
                              context_instance=RequestContext(request))
            except:
                user_form = UserCreationForm()
                return render(request,
                              'blog/add_person.html',
                              {'user_form': user_form},
                              context_instance=RequestContext(request))
    else:
        post_form = PostForm()
    ctx = {'post_form': post_form}
    return render(render,
                  'blog/add_post.html',
                  ctx, context_instance=RequestContext(request))


def loginn(request):
    def errorHandle(error):
        form = LoginForm()
        return render_to_response('blog/login.html', {
            'error': error,
            'form': form,
        }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,
                                password=password)
            if user is not None:
                if user.is_active:

                    login(request, user)
                    user_profile = get_object_or_404(UserProfile, user=user.id)
                    print user_profile
                    return HttpResponseRedirect('/profile')
                    # return render(request, 'blog/profile.html', {
                    #     'user': user,'user_p': user_profile,
                    # }, context_instance=RequestContext(request))
                else:
                    # Return a 'disabled account' error message

                    error = ugettext('account disabled')
                    return errorHandle(error)
            else:
            # Return an 'invalid login' error message.
                error = ugettext('invalid login')
                return errorHandle(error)
        else:
            error = ugettext('form is invalid')
            return errorHandle(error)
    else:
        form = LoginForm()
        return render(request, 'blog/login.html', {
            'form': form,
        }, context_instance=RequestContext(request))


def confirm(request, c_code):
    if confirm_email(c_code):
        msg = ugettext("Your email is verified")
    else:
        msg = ugettext("Your email is not verified")
    return render(request, 'blog/conf.html',
                           {'ccode': msg, },
                 context_instance=RequestContext(request))


def activate(request, c_code):
    if confirm_comment(c_code):
        msg = ugettext("Your comment is activated")
    else:
        msg = ugettext("Your comment can not be activated")
    return render(request, 'blog/conf.html', {
        'ccode': msg, }, context_instance=RequestContext(request))


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


def posts(request):
    posts = Post.objects.order_by('-id')
    t = get_template('blog/allposts.html')
    html = t.render(Context({'posts': posts,
                             'user': request.user, }))
    return HttpResponse(html)


def my_posts(request):
    posts = Post.objects.filter(userid=request.user)
    t = get_template('blog/myposts.html')
    html = t.render(Context({'posts': posts,
                             'user': request.user, }))
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
        """

        :param user_id:
        :return:
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


@login_required(login_url='/login/')
def update_user(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user.id)
    if request.method != "POST":
        return render(request, 'blog/profile.html',
                      {'user': user, 'user_p': user_profile, },
                      context_instance=RequestContext(request))

    if request.method == "POST":
        data = request.POST
        data2 = request.FILES
        user.first_name = data.get("name")
        user.last_name = data.get("lname")
        user.save()
        user_profile.interests = data.get("int")
        try:
            user_profile.image.delete(save=False)
        except:
            pass
        try:
            user_profile.image = data2["image"]
            user_profile.save()
            resize_image.delay(user_profile.image)
        except:
            pass
    return render(request, 'blog/profile.html',
                  {'user': user,
                   'user_p': user_profile, },
                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def change_password(request):
    user = request.user
    data = request.POST
    error = ugettext('Password was changed')
    if request.method != "POST":
        return render(request, 'blog/changepassword.html',
                      {'user': user, },
                      context_instance=RequestContext(request))
    if request.method == "POST":

        if user.check_password(data.get("old_pass")):

            if data.get("pass1") == data.get("pass2"):

                if data.get("pass2") != "":
                    user.set_password(data.get("pass1"))
                    user.save()
                else:
                    error = ugettext("Passwords must not be null")
            else:
                error = ugettext('passwords are not matching')
        else:
            error = ugettext('wrong password ')

    return render(request, 'blog/changepassword.html',
                  {'user': user, 'error': error},
                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def change_email(request):
    user = request.user
    error = ugettext('Email Changed, Please Confirm Your E-mail ')
    form = UserCreationForm(request.POST)
    if request.method != "POST":
        return render(request, 'blog/email.html', {'userf': form, },
                      context_instance=RequestContext(request))
    if request.method == "POST":
        data = request.POST
        email = data.get("email")
        if email_re.match(email):

            if User.objects.get(email=email):
                messages.warning("You can not use this e-mail")
                return render(request,
                              'blog/email.html',
                              {'userf': form, 'user': request.user, },
                              context_instance=RequestContext(request))
            else:
                user.is_active = 0
                user.email = email
                user.save()
                c_code = produce_val()
                send.delay(c_code, email)
                user_pr = UserProfile.objects.get(user=user)
                user_pr.conf_code = c_code
                user_pr.exp_date = datetime.now()
                user_pr.save()
                messages.success(request, 'Email has been Changed .')
                return render(request, 'blog/email.html',
                              {'userf': form,
                               'error': error,
                               'user': request.user, },
                              context_instance=RequestContext(request))
        else:
            messages.error(request, "Enter a valid email")
    return render(request,
                  'blog/email.html',
                  {'userf': form,
                   'user': request.user, },
                  context_instance=RequestContext(request))


@register.inclusion_tag('blog/children.html')
def subcomment_tag(parent, sub):
    parent = parent
    sub = sub
    return {'parent': parent, 'subs': sub, }


def dnm(request, post_id):
    """

    :param request:
    :param post_id:
    :return:
    """
    post = get_object_or_404(Post, pk=post_id)
    parents = post.item.all()
    content = ContentType.objects.get_for_model(Comment)
    subs = Comment.objects.filter(content_type=content).filter(is_active=1).filter(parent=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            email = form.cleaned_data["email"]
            c_type = request.POST.get("c_type")
            obj_id = request.POST.get("replyfor")

        if c_type == "Comment":
            c_model = Comment

        if c_type == "Post":
            c_model = Post

            con_type = ContentType.objects.get_for_model(c_model)
            new_comment = Comment(email=email,
                                  text=text,
                                  content_type=con_type,
                                  parent=post_id,
                                  object_id=obj_id,
                                  pubdate=datetime.now(),
                                  is_active=0)
            new_comment.save()

            if request.user.is_authenticated():
                new_comment.is_active = 1
                new_comment.user = request.user
                new_comment.save()
            else:

                if email_check(email):
                    return HttpResponseRedirect('/')
                else:
                    act_code = produce_val()
                    send_act_code.delay(act_code,
                                        new_comment.email)
                    new_activation = Activation(conf_code=act_code,
                                                comment=new_comment,
                                                exp_date=datetime.now(), )
                    new_activation.save()
        form = CommentForm()
    else:
        form = CommentForm()

    return render(request, 'blog/deneme.html', {'parents': parents,
                                                'subs': subs, 'post': post,
                                                'r_user': request.user,
                                                'form': form, },
                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def email_check(email):
    try:
        User.objects.get(email=email)
        return 0
    except:
        return 1

