from blogs import views
from django.conf.urls import patterns, url
from django.contrib import admin
admin.autodiscover()
import settings
from django.conf.urls import patterns, include, url
urlpatterns = patterns('',
    (r'^ckeditor/', include('ckeditor.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^blog/$', views.index, name='index'),
    url(r'^add/$', views.add_person, name='add_person'),

    url(r'^addpost/$', views.add_post, name='add_post'),
    url(r'^posts/$', views.show_post, name='show_post'),
    #url(r'^addpost/$', views.post, name='post'),
    #url(r'^adde/$', views.add_entry, name='add_entry'),
    url(r'^login/$', views.loginn, name='login'),
    url(r'^confirm/$', views.confirm, name='confirm'),
    url(r'^(?P<ccode>.+)/confirm/$', views.conf2, name='conf2'),
    url(r'^(?P<ccode>.+)/activate/$', views.activate, name='activate'),
    url(r'^ps/$', views.posts, name='post'),
    url(r'^(?P<post_id>.+)/showpost/$', views.show_post2, name='show_post'),

)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
)