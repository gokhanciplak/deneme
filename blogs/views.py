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



# messages.debug(request, '%s SQL statements were executed.' % count)
# messages.info(request, 'Three credits remain in your account.')
# messages.success(request, 'Profile details updated.')
# messages.warning(request, 'Your account expires in three days.')
# messages.error(request, 'Document deleted.')

def add_person(request):
    success = False
    if request.method == "POST":
        user_form = UserCreationForm(request.POST, request.FILES)
        if user_form.is_valid():
            success = True
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            username = produce_val()
            password = user_form.cleaned_data['password1']
            password_t = user_form.cleaned_data['password2']
            email = user_form.cleaned_data['email']
            image = user_form.cleaned_data['image']
            if password != password_t:
                error = ugettext('Passwords have to be same')
                return render_to_response('blog/add_person.html', {'user_form': user_form,
                                                                   'error': error},
                                          context_instance=RequestContext(request))
            try:
                User.objects.get(email=email)
                error = ugettext('This e-mail was already in use')
                return render_to_response('blog/add_person.html', {'user_form': user_form, 'error': error},
                                          context_instance=RequestContext(request))
            except:
                new_user = User(first_name=first_name, last_name=last_name, username=username,
                                email=email, is_active=0, is_staff=0, is_superuser=0,
                                date_joined=datetime.now())
                new_user.set_password(password)
                new_user.save()
                c_code = produce_val() #producing confirmation code
                send.delay(c_code, email)
                user = new_user.id
                new_profile = UserProfile(user_id=user, image=image, conf_code=c_code, exp_date=datetime.now())
                new_profile.save()
                return HttpResponseRedirect('/login/')

    else:
        user_form = UserCreationForm()
    ctx = {'user_form': user_form}
    return render(request, 'blog/add_person.html', ctx, context_instance=RequestContext(request))


@login_required(login_url='/login')
def add_post(request):
    if request.method == "POST":
        print "post"
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            print "valid"
            title = post_form.cleaned_data['title']
            keywords = post_form.cleaned_data['keywords']
            description = post_form.cleaned_data['description']
            image = post_form.cleaned_data['image']
            text = post_form.cleaned_data['text']
            slug = title
            print image
            try:
                new_post = Post(title=title, userid=request.user, slug=slug, keywords=keywords,
                                image=image, text=text, description=description,
                                date=datetime.now())
                new_post.save()
                post_form = PostForm()

                ctx = {'post_form': post_form}
                return render(request, 'blog/add_post.html', ctx, context_instance=RequestContext(request))
            except:
                err="except"
                user_form = UserCreationForm()
                ctx = {'user_form': user_form}
                return render(request, 'blog/add_person.html', ctx, context_instance=RequestContext(request))
    else:
        post_form = PostForm()
    ctx = {'post_form': post_form}
    return render(render, 'blog/add_post.html', ctx, context_instance=RequestContext(request))


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = post.item.all()

    comments_of_comment = Comment.objects.filter(content_type_id=10, )



    # for i in range (item.__len__()):
    #     try:
    #         comments_of_comment.append(Comment.objects.get(content_type_id=10, object_id=item[i].id))
    #     except:
    #         pass

    t = get_template('blog/posts.html')
    html = t.render(Context({'post': post, 'post_comments': comment, 'cc': comments_of_comment, }, ))
    return HttpResponse(html)


def show_post2(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments_of_post = post.item.all()
    id_list = []
    for i in range (comments_of_post.__len__()):
        id_list.append(comments_of_post[i].id)
    my_list = []
    for x in id_list:
        my_list.append(x)
        #to get only comments of comments which are made post i am listing on the page
    comments_of_comment = Comment.objects.filter(content_type_id=10).filter(object_id__in=my_list).filter(is_active=1)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            email = form.cleaned_data["email"]
            c_type = request.POST.get("c_type")
            obj_id = request.POST.get("replyfor")
            print email
            if c_type == "Comment":
                c_model = Comment
            if c_type == "Post":
                c_model = Post
            con_type = ContentType.objects.get_for_model(c_model)
            new_comment = Comment(email=email, text=text, content_type=con_type, object_id=obj_id,
                                  pubdate=datetime.now(), is_active=0)
            new_comment.save()

            if request.user.is_authenticated():
                new_comment.is_active = 1
                new_comment.user = request.user
                new_comment.save()
            else:
                act_code = produce_val()
                send_act_code.delay(act_code, new_comment.email)
                print act_code
                new_activation = Activation(conf_code=act_code, comment=new_comment,
                                            exp_date=datetime.now(), )
                new_activation.save()
        form = CommentForm()
    else:
        form = CommentForm()

    user = request.user
    return render(request, 'blog/posts.html', {'post': post, 'post_comments': comments_of_post,
                                               'cc': comments_of_comment, 'form': form, 'user': user},
                  context_instance=RequestContext(request))


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
        form = LoginForm() # An unbound form
        return render(request, 'blog/login.html', {
            'form': form,
        }, context_instance=RequestContext(request))


def confirm(request):
    return render_to_response('blog/confirm.html', {

    }, context_instance=RequestContext(request))


def conf2(request, c_code):
    if confirm_email(c_code):
        msg = ugettext("Your email is verified")
    else:
        msg = ugettext("Your email is not verified")
    return render(request, 'blog/conf.html', {
        'ccode': msg, },
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
    html = t.render(Context({'posts': posts, 'user':request.user,}))
    return HttpResponse(html)


def my_posts(request):
    posts = Post.objects.filter(userid=request.user)
    t = get_template('blog/myposts.html')
    html = t.render(Context({'posts': posts, 'user':request.user,}))
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
            img = resize_image.delay(user_profile.image)
        except:
            pass
    return render(request, 'blog/profile.html', {'user': user, 'user_p': user_profile, },
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

    return render(request, 'blog/changepassword.html', {'user': user, 'error': error},
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
            try:
                User.objects.get(email=email)
                messages.warning("You can not use this e-mail")
                return render(request, 'blog/email.html', {'userf': form, 'user': request.user,},
                              context_instance=RequestContext(request))
            except:
                user.is_active = 0
                user.email = email
                user.save()
                c_code = produce_val() #producing confirmation code
                send.delay(c_code, email)
                user_pr = UserProfile.objects.get(user=user)
                user_pr.conf_code = c_code
                user_pr.exp_date = datetime.now()
                user_pr.save()
                messages.success(request, 'Email has been Changed .')
                return render(request, 'blog/email.html', {'userf': form, 'error': error, 'user': request.user,},
                              context_instance=RequestContext(request))
        else:
            messages.error(request,"Enter a valid email")
    return render(request, 'blog/email.html',
                  {'userf': form, 'user': request.user,},
                  context_instance=RequestContext(request))


@register.inclusion_tag('blog/children.html')
def subcomment_tag(parent , sub):
    parent = parent
    sub = sub

    return {'parent': parent, 'subs': sub, }


def dnm(request, post_id):
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
            print email
            if c_type == "Comment":
                c_model = Comment
            if c_type == "Post":
                c_model = Post
            con_type = ContentType.objects.get_for_model(c_model)
            new_comment = Comment(email=email, text=text, content_type=con_type, parent=post_id, object_id=obj_id,
                                  pubdate=datetime.now(), is_active=0)
            new_comment.save()

            if request.user.is_authenticated():
                new_comment.is_active = 1
                new_comment.user = request.user
                new_comment.save()
            else:
                act_code = produce_val()
                send_act_code.delay(act_code, new_comment.email)
                print act_code
                new_activation = Activation(conf_code=act_code, comment=new_comment,
                                            exp_date=datetime.now(), )
                new_activation.save()
        form = CommentForm()
    else:
        form = CommentForm()

    return render(request, 'blog/deneme.html', {'parents': parents, 'subs': subs, 'post': post,
                                                'r_user': request.user, 'form': form, },
                  context_instance=RequestContext(request))

