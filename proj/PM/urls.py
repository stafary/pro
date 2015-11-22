from django.conf.urls import patterns, include, url
from django.contrib import admin
from mypm.views import login,empty,register,home,show_pic
import settings
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'PM.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login),
    url(r'^accounts/register/$',register),
    url(r'^$',empty),
    url(r'^home/$',home),
    url( r'^static/(?P<path>.*)$', 'django.views.static.serve',
        { 'document_root':settings.STATIC_URL }),
    url( r'^pic_folder/(?P<path>.*)$', 'django.views.static.serve',
        { 'document_root':settings.STATIC_URL2 }),
    url(r'^mypic/$', show_pic),

)
