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
def home(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")
    if request.method == 'POST':
             form = ImageUploadForm( request.POST, request.FILES )
             n = request.FILES['image'].name
             if form.is_valid():
                  pic = form.cleaned_data['image']
                  m = picture(image = pic,name = n,username=request.user.username)
                  m.save()
                  src = "pic_folder/" + n
                  pic = Image.open(src)
                  
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
                          m.place = u"外星"
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
                          if(flag):
                              bm = xBaiduMap()
                              add = bm.getAddress(ln, lt)
                              m.place = add
                      m.save()
                  return HttpResponseRedirect("/up_success?flag=%s"%flag)    
             return	render_to_response("home.html",{"form":form})
    form = ImageUploadForm()
    return	render_to_response("home.html",{"form":form})

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
    place = request.GET.get("place")
    pictures = picture.objects.filter(place=place,username=request.user.username)
    if request.method =="POST":
        for pic in pictures:
            if(request.POST.has_key(str(pic.name))):
                if(request.POST[pic.name]==u"确认修改"):
                    pic.comment = request.POST["changed_comment"]
                    pic.save()
                else:
                    pic.image.delete()
                    picture.objects.filter(name= pic.name)[0].delete()
        pictures = picture.objects.filter(place=place,username=request.user.username)
#        return HttpResponseRedirect("/all_of_one/?place=%s"%place)
    return render_to_response("all_of_one.html",{"pictures":pictures,"place":place})
    
    

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

def show_pic(request):
    if request.POST:
        if request.POST["place"]=="":
            commen=request.POST["comment"]
            pics=picture.objects.filter(username=request.user.username, commen__contains=commen)
            loca=[]
            loca2=[]
            for i in pics:
                if i.place not in loca2:
                    loca2.append(i.place)
                    loca.append({"pic":i.name, "place":i.place})
            return render_to_response("search.html",{"locas":loca})
        else:
            place=request.POST["place"]
            pics=picture.objects.filter(username=request.user.username, place__contains=place)
            loca=[]
            loca2=[]
            for i in pics:
                if i.place not in loca2:
                    loca2.append(i.place)
                    loca.append({"pic":i.name, "place":i.place})
            return render_to_response("search.html",{"locas":loca})
    else:
        pics = picture.objects.filter(username=request.user.username)
        loca=[]
        loca2=[]
        for i in pics:
            if i.place not in loca2:
                loca2.append(i.place)
                loca.append({"pic":i.name, "place":i.place})
        c=Context({"locas": loca})
        print c
        return render_to_response("places.html", c)
