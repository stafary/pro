from django.shortcuts import render,HttpResponseRedirect,HttpResponse,\
render_to_response
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from forms import ImageUploadForm
from models import picture
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
@login_required
def home(request):
	if request.method == 'POST':
		form = ImageUploadForm( request.POST, request.FILES )
		if form.is_valid():
			m = picture(image = form.cleaned_data['image']) 
			m.save()
			return HttpResponse('image upload success')
	return	render_to_response("home.html")

def large(request):
    return render_to_response("large.html")