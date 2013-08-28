from blogs import views
from django.conf.urls import patterns, url
from django.contrib import admin
admin.autodiscover()
import settings
from django.conf.urls import patterns, include, url
handler404 = 'blog.view.handler404'
handler500 = 'blog.view.handler500'
urlpatterns = patterns('',
    (r'^ckeditor/', include('ckeditor.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add/$', views.add_person, name='add_person'),
    url(r'^profile/$', views.update_user, name='update_user'),
    url(r'^addpost/$', views.add_post, name='addpost'),
    url(r'^myposts/$', views.my_posts, name='myposts'),
    url(r'^posts/$', views.show_post, name='show_post'),
    url(r'^login/$', views.loginn, name='login'),
    url(r'^confirm/$', views.confirm, name='confirm'),
    url(r'^(?P<c_code>.+)/confirm/$', views.conf2, name='conf2'),
    url(r'^(?P<c_code>.+)/activate/$', views.activate, name='activate'),
    url(r'^$', views.posts, name='post'),
    # url(r'^showpost/(?P<post_id>.+)/$', views.show_post2, name='show_post'),
    url(r'^changep/$', views.change_password, name='change_password'),
    url(r'^changee/$', views.change_email, name='change_email'),
    # url(r'^dnm/$', views.dnm, name='dnm'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^dnm/(?P<post_id>.+)/$', views.dnm, name='dnm'),

)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
)