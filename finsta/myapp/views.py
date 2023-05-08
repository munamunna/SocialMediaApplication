from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect
from myapp.forms import SignUpForm,LoginForm,ProfileEditForm,PostForm
from myapp.models import UserProfile,Posts,Comments

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.views.generic import CreateView,View,TemplateView,UpdateView,ListView
from django.contrib import messages
from django.urls import reverse_lazy



# Create your views here.
class Indexview(CreateView,ListView):
    
    template_name="index.html"
    form_class=PostForm
    model=Posts
    success_url=reverse_lazy("index")
    context_object_name="posts"
    def form_valid(self, form):
        form.instance.user=self.request.user
        return super().form_valid(form)

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
# localhost:8000/posts{id}/like/
def add_like_view(request,*args,**kargs):
    id=kargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    post_obj.liked_by.add(request.user)
    return redirect("index")

# localhost:8000/posts/{id}/comments/add/
def add_comment_view(request,*args,**kargs):
    id=kargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    comment=request.POST.get("comment")
    user=request.user
    Comments.objects.create(user=user,comment_text=comment,post=post_obj)
    return redirect("index")
    
# localhost:8000/Comments{id}/remove/
def remove_comment_view(request,*args,**kargs):
    id=kargs.get("pk")
    comment_obj=Comments.objects.get(id=id)
    if request.user == comment_obj.user:
        comment_obj.delete()
        return redirect("index")
    else:
        messages.error(request,"pls contact admin")
        return redirect("signin")