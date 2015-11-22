#coding=utf-8
from django import forms
class ImageUploadForm(forms.Form): 
	"""Image upload form.""" 
	image = forms.ImageField(label=u"上传照片:")
      