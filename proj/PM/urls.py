from django.conf.urls import patterns, include, url
from django.contrib import admin
from mypm.views import login,empty,register,home,up_success,all_of_one,show_pic,search_comment,large,next_pic,ahead_pic,search_place
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
    url(r'^up_success/$',up_success),
    url(r'^all_of_one/$',all_of_one),
    url(r'^mypic/$', show_pic),
    url(r'^search_com/$',search_comment),
    url(r'^search_place/$',search_place),    
    url(r'^large/$',large),
#    url(r'edit_pic/$',edit_pic),
#    url(r'edit_pic_rotate/$',edit_pic_rotate),
#    url( r'^new/(?P<path>.*)$', 'django.views.static.serve',
#        { 'document_root':settings.STATIC_URL3 }),
    url(r'^large/next/$',next_pic),
    url(r'^large/ahead/$',ahead_pic),
)
