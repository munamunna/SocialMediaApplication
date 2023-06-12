from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect
from myapp.forms import SignUpForm,LoginForm,ProfileEditForm,PostForm,CoverpicForm
from myapp.models import UserProfile,Posts,Comments

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.views.generic import CreateView,View,TemplateView,UpdateView,ListView,DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils.decorators import method_decorator

def signin_required(fn):
    def wrapper(request,*args,**kargs):
        if not request.user.is_authenticated:
            messages.error(request,"you must login to perform this action")
            return redirect("signin")
        return fn(request,*args,**kargs)
    return wrapper


# Create your views here.
@method_decorator(signin_required,name="dispatch")
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

@method_decorator(signin_required,name="dispatch") 
class ProfileEditView(UpdateView):
    form_class=ProfileEditForm
    template_name="profileedit.html"
    model=UserProfile
    success_url=reverse_lazy("index")
# localhost:8000/posts{id}/like/
@signin_required
def add_like_view(request,*args,**kargs):
    id=kargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    post_obj.liked_by.add(request.user)
    return redirect("index")

# localhost:8000/posts/{id}/comments/add/
@signin_required
def add_comment_view(request,*args,**kargs):
    id=kargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    comment=request.POST.get("comment")
    user=request.user
    Comments.objects.create(user=user,comment_text=comment,post=post_obj)
    return redirect("index")
    
# localhost:8000/Comments{id}/remove/
@signin_required
def remove_comment_view(request,*args,**kargs):
    id=kargs.get("pk")
    comment_obj=Comments.objects.get(id=id)
    if request.user == comment_obj.user:
        comment_obj.delete()
        return redirect("index")
    else:
        messages.error(request,"pls contact admin")
        return redirect("signin")

@method_decorator(signin_required,name="dispatch")   
class ProfileDetailview(DetailView):
    model=UserProfile
    template_name="profile.html"
    context_object_name="profile"

# profiles/{id}/coverpic/change
@signin_required
def change_cover_pic_view(request,*args,**kargs):
    id=kargs.get("pk")
    prof_obj=UserProfile.objects.get(id=id)
    form=CoverpicForm(instance=prof_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profiledetail",pk=id)
    return redirect("profiledetail",pk=id)

# class ProfileListview(ListView):
#     model=UserProfile
#     template_name="profile-list.html"
#     context_object_name="profiles"
    
#     def get_queryset(self):
#         return UserProfile.objects.exclude(user=self.request.user)
        
@method_decorator(signin_required,name="dispatch")
class ProfileListView(ListView):
    model=UserProfile
    template_name="profile-list.html"
    context_object_name="profiles"
   
    def get_queryset(self):
        return UserProfile.objects.exclude(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        pname = request.POST.get('username')
        qs = UserProfile.objects.filter(
            Q(user__username__icontains=pname) | 
            Q(user__first_name__icontains=pname) | 
            Q(user__last_name__icontains=pname)
        )
        return render(request,self.template_name,{"profiles":qs})

    #change queryset
    # def get(self,request,*args,**kargs):
    #     qs=UserProfile.objects.exclude(user = request.user)
    #     return render(request,self.template_name,{"profiles":qs})









# localhost:8000/profiles/{id}/follow/
@signin_required
def follow_view(request,*args,**kargs):
    id=kargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    user_prof=UserProfile.objects.get(user=request.user)
    user_prof.following.add(profile_obj)
    user_prof.save()
    
    return redirect("index")

@signin_required
def unfollow_view(request,*args,**kargs):
    id=kargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    user_prof=UserProfile.objects.get(user=request.user)
    user_prof.following.remove(profile_obj)
    user_prof.save()
    return redirect("index")

def sign_out_view(request,*args,**kargs):
    logout(request)
    return redirect("signin")

