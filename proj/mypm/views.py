#coding=utf-8
from django.shortcuts import render,HttpResponseRedirect,HttpResponse,\
render_to_response
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from forms import ImageUploadForm
from models import picture
import urllib2,urllib,httplib
import json
from PIL import Image
from PIL.ExifTags import TAGS
from django.template import Context
from StringIO import StringIO
import sae
import copy
from sae.ext.storage import monkey

def login(request):
    if request.method == "POST":
        if request.POST.get("log"):
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                # Correct password, and the user is marked "active"
                auth.login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect("/home/")
            else:
                # Show an error page
               return render_to_response("login.html",{"error":True,"username":\
               username,"password":password})
        else:
            return HttpResponseRedirect("/accounts/register/")
    else:
        return render_to_response("login.html",{"error":False})
def empty(request):
    return HttpResponseRedirect("/accounts/login/")
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/accounts/login/")
    else:
        form = UserCreationForm()
    return render_to_response("reg.html", {'form': form,})
def xiuxiu_upload(request):
    if request.method == 'POST':
        images= request.FILES.getlist('images')
        image = images[0]
        place = request.GET["place"]
        username = request.GET["username2"]
        pic_id = request.GET["picid2"]
        m = picture(image = image,name = image.name,username=username,place=place)
#        m = picture(image=image, username="4",place=u"成都")
        m.save()
        request.session["id_after_beautify"] = m.id
        m.src = "http://photomanage-picfolder2.stor.sinaapp.com/pic_folder%2F"+str(m.image)[11:]
        m.save()
        pic_del = picture.objects.get(id =pic_id)
        pic_del.image.delete()
        pic_del.delete()
       
        return HttpResponse("success")
    else:
        return render_to_response("xiuxiu_Upload.html")
def home(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")
    if request.method == 'POST':
        images= request.FILES.getlist('images')
        flag2 = True
        for image in images:
            n = image.name
            m = picture(image = image,name = n,username=request.user.username)
            m.save()
            m.src = "http://photomanage-picfolder2.stor.sinaapp.com/pic_folder%2F"+str(m.image)[11:]
            m.save()
            c = sae.storage.Connection()
            bucket = c.get_bucket('picfolder2')
            path = unicode(str(m.image),"utf-8")
            srcx = bucket.get_object_contents(path)
            pic = Image.open(StringIO(srcx))
            m.place = u"外星"
            try:
                if hasattr(pic, '_getexif' ):
                    ret = {}
                    exifinfo = pic._getexif()
                    flag = True
                    for tag, value in exifinfo.items():
                        decoded = TAGS.get(tag, tag)
                        ret[decoded] = value
                    try:
                        xy = ret["GPSInfo"]
                    except:
                        flag = False
                        flag2 = False
                          
                    if(flag):
                        try:
                            lt = xy[4][0][0]*1.0/xy[4][0][1]+\
                            xy[4][1][0]*1.0/xy[4][1][1]/60+xy[4][2][0]*1.0\
                            /xy[4][2][1]/3600
                            ln = xy[2][0][0]*1.0/xy[2][0][1]+\
                            xy[2][1][0]*1.0/xy[2][1][1]/60+xy[2][2][0]*1.0\
                            /xy[2][2][1]/3600
                        except:
                            flag =False
                            flag2 = False
                        if(flag):
                            bm = xBaiduMap()
                            add = bm.getAddress(ln, lt)
                            start = False
                            add2=""
                            for char in add:
                                if(char==u"市" or char==u"县"):
                                    break
                                if(start):
                                    add2+=char
                                if(char == u"省" or char == u"区"):
                                    start = True
                            if(add2):
                                m.place = add2                             
                    m.save()
                else:
                    m.save()
            except:
                flag2 = False
                m.save()
        return render_to_response("home.html",{"up":True,"flag":flag2})    
    return	render_to_response("home.html")
def up_success(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")
    flag = request.GET.get("flag")
    if(flag == "True"):
        flag = True
    else:
        flag = False
    return render_to_response("up_success.html",{"flag":flag})
def all_of_one(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")
    if(request.GET.has_key("place2") and request.GET["place2"]!=""):
        return HttpResponseRedirect("/search_place/?place=%s"%request.GET.get("place2"))
    if(request.GET.has_key("comment") and request.GET["comment"]!=""):
        return HttpResponseRedirect("/search_com/?comment=%s"%request.GET.get("comment"))
    place = request.GET.get("place")
    pictures = picture.objects.filter(place=place,username=request.user.username)
    if request.method =="POST":
            for pic in pictures:
                if(request.POST.has_key(str(pic.id))):
                    if(request.POST[str(pic.id)]==u"确认修改"):
                        pic.comment = request.POST["changed_comment"]
                        pic.save()
                    else:
                        pic.image.delete()
                        pic.delete()
            pictures = picture.objects.filter(place=place,username=request.user.username)

    return render_to_response("all_of_one.html",{"pictures":pictures,"place":place})

def search_comment(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")
    comment = request.GET.get("comment")
    pictures = picture.objects.filter(username=request.user.username,comment__contains=comment)
    if request.method =="POST":
            for pic in pictures:
                if(request.POST.has_key(str(pic.id))):
                    if(request.POST[str(pic.id)]==u"确认修改"):
                        pic.comment = request.POST["changed_comment"]
                        pic.save()
                    else:
                        pic.image.delete()
                        picture.objects.get(id= pic.id).delete()
            pictures = picture.objects.filter(username=request.user.username,comment__contains=comment)
    return render_to_response("search_com.html",{"pictures":pictures,"comment":comment})
def search_place(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")
    place=request.GET.get("place")
    pics=picture.objects.filter(username=request.user.username, place__contains=place)            
    loca=[]
    loca2=[]
    for i in pics:
        if i.place not in loca2:
            loca2.append(i.place)
            loca.append({"pic":i.src, "place":i.place})
    return render_to_response("search_place.html",{"locas":loca,"place":place})
def show_pic(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")

    if request.POST:
        if request.POST["place"]=="":
            commen=request.POST["commen"]
            return HttpResponseRedirect("/search_com/?comment=%s"%commen)
        else:
            return HttpResponseRedirect("/search_place/?place=%s"%request.POST["place"])

    else:
        pics = picture.objects.filter(username=request.user.username)
        loca=[]
        loca2=[]
        for i in pics:
            if i.place not in loca2:
                loca2.append(i.place)
                loca.append({"pic":i.src, "place":i.place})
        c=Context({"locas": loca})
        return render_to_response("places.html", c)

#给出经纬度，调用百度地图获得照片的拍摄城市
class xBaiduMap:
    def __init__(self,key='UWVFoZBvfQKRCRYPQUGcjDoC'):
        self.host='http://api.map.baidu.com'
        self.path='/geocoder?'
        self.param={'address':None,'output':'json','key':key,'location':None,'city':None}
      
    def getLocation(self,address,city=None):
        rlt=self.geocoding('address',address,city)
        if rlt!=None:
            l=rlt['result']
            if isinstance(l,list):
                return None
            return l['location']['lat'],l['location']['lng']
        
    def getAddress(self,lat,lng):
        rlt=self.geocoding('location',"{0},{1}".format(lat,lng))
        if rlt!=None:
            l=rlt['result']
            return l['formatted_address']
            #Here you can get more details about the location with 'addressComponent' key
            #ld=rlt['result']['addressComponent']
            #print(ld['city']+';'+ld['street'])
            #
    def geocoding(self,key,value,city=None):
        if key=='location':
            if 'city' in self.param:
                del self.param['city']
            if 'address' in self.param:
                del self.param['address']
            
        elif key=='address':
            if 'location' in self.param:
                del self.param['location']
            if city==None and 'city' in self.param:
                del self.param['city']
            else:
                self.param['city']=city
        self.param[key]=value
        r=urllib.urlopen(self.host+self.path+urllib.urlencode(self.param))
        rlt=json.loads(r.read())
        if rlt['status']=='OK':
            return rlt
        else:
            print "Decoding Failed"
            return None

def large(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")
    pic_id = request.GET.get("id")
    request.session['id'] = pic_id
    pic = picture.objects.get(id = pic_id)
    if request.method =="POST":
        pic.comment = request.POST["changed_comment"]
        pic.save()
#    return HttpResponse("%s"%pic.src)
    return render_to_response("large.html",{"pic":pic})
    
def large_after_beautify(request):
    pic_id = request.session["id_after_beautify"]
    request.session['id'] = pic_id
    pic = picture.objects.get(id = pic_id)
#    return HttpResponse("%s"%pic.src)
    return render_to_response("large.html",{"pic":pic})    
def next_pic(request):
    pic_id = request.session['id']
    pic = picture.objects.get(id = pic_id)
    pic_place = pic.place
    user_name = pic.username
    album_usr = picture.objects.filter(username = user_name)
    album = album_usr.filter(place = pic_place)
    for i in range(0,len(album)):
        if int(album[i].id) == int(pic_id):
            request.session['counter'] = i
            break;
    counter = request.session['counter']
    if counter != len(album) + 1:
        try:
            request.session['id'] = album[counter+1].id        
            request.session['counter'] = i+1
            request.session['id'] = album[counter+1].id
            pic_id = album[counter+1].id
            pic = picture.objects.get(id = pic_id)
            return render_to_response("large.html",{"pic":pic})        
        except IndexError:
            return render_to_response("last.html",{"pic":pic})        
    else:
        return render_to_response("last.html",{"pic":pic})        
    return render_to_response("last.html",{"pic":pic})        
def ahead_pic(request):
    pic_id = request.session['id']
    pic = picture.objects.get(id = pic_id)
    pic_place = pic.place
    user_name = pic.username
    album_usr = picture.objects.filter(username = user_name) 
    album = album_usr.filter(place = pic_place)
    for i in range(0,len(album)):
        if int(album[i].id) == int(pic_id):
            request.session['counter'] = i
            break;
    counter = request.session['counter']
    if counter != 0:
        try:
            request.session['id'] = album[counter-1].id        
            request.session['counter'] = i-1
            request.session['id'] = album[counter-1].id
            pic_id = album[counter-1].id
            pic = picture.objects.get(id = pic_id)
            return render_to_response("large.html",{"pic":pic})        
        except IndexError:
            return render_to_response("first.html",{"pic":pic})        
    else:
        return render_to_response("first.html",{"pic":pic})        
    return render_to_response("first.html",{"pic":pic})        

def beautify(request):
    pic_id = request.GET.get("id")
    request.session['id'] = pic_id
    pic = picture.objects.get(id = pic_id)
#    return HttpResponse("%s"%pic.src)
    return render_to_response("beautify2.html",{"pic":pic})
def cross(request):
    return render_to_response('crossdomain.xml',content_type='text/xml')
def jsp(request):
    return render_to_response('xx.html')