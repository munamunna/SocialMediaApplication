from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect
from myapp.forms import SignUpForm,LoginForm,ProfileEditForm
from myapp.models import UserProfile

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.views.generic import CreateView,View,TemplateView,UpdateView
from django.contrib import messages
from django.urls import reverse_lazy



# Create your views here.
class Indexview(TemplateView):
    
    template_name="index.html"

class SignUpView(CreateView):
    model=User
    form_class=SignUpForm
    template_name="register.html"
    success_url=reverse_lazy("register")

    def form_valid(self, form):
        messages.success(self.request,"account has been created")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request,"failed to create account")
        return super().form_invalid(form)

class SigninView(View):
    model=User
    template_name="login.html"
    form_class=LoginForm

    def get(self,request,*args,**kargs):
        form=self.form_class
        return render(request,self.template_name,{"form":form})
    
    def post(self,request,*args,**kargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            usname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=usname,password=pwd)
            if usr:
                login(request,usr)
                messages.success(request,"login success")
                return redirect("index")
            messages.error(request,"invalid credential")
            return render(request,self.template_name,{"form":form})

class ProfileEditView(UpdateView):
    form_class=ProfileEditForm
    template_name="profileedit.html"
    model=UserProfile
    success_url=reverse_lazy("index")
    
