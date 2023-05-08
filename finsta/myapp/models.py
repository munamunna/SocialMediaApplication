from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    profile_pic=models.ImageField(upload_to="profilepics",blank=True,default="/profilepics/deafault.jpg")
    bio=models.CharField(max_length=200,null=True)
    address=models.CharField(max_length=200,null=True)
    dob=models.DateTimeField(null=True)
    # symmetrical=false means  user followed person not possible to automatically refollow
    following=models.ManyToManyField("self",related_name="followed_by",symmetrical=False)
    created_date=models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username
# profile_obj.following.add(profile_obj)
# profile_obj.following.all()
    
class Posts(models.Model):
    title=models.CharField(max_length=200)
    image=models.ImageField(upload_to="postimages",null=True,blank=True)
    # post uploaded user
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_posts")
    created_date=models.DateTimeField(auto_now_add=True)
    liked_by=models.ManyToManyField(User,related_name="post_like")

    def __str__(self):
        return self.title
# post_obj.liked_by.add(model instance)
# post_obj.liked_by.all()
    
class Comments(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    comment_text=models.CharField(max_length=200)
    post=models.ForeignKey(Posts,on_delete=models.CASCADE,related_name="post_comment")
    created_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_text


# to create a blank profile before registration we use the concept signals
# django signals-post_save,pre_save,post_delete,pre_delete

# fuction after registration is(that is after create user object in Usermodel)
# here (instance)-which user who is going to create profile
def create_profile(sender,instance,created,**kargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_profile,sender=User)
        
