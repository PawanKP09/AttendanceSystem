import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext as _
from django.dispatch import receiver

class TimeStampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class User(AbstractUser, TimeStampModel):
    Uid = models.CharField(max_length=20,null=True,blank=True)
    profile_image = models.FileField(upload_to='profile_images',null=True,blank=True)

    def __str__(self):
        return self.username


class Logs(TimeStampModel):
    in_time = models.TimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    out_time = models.TimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    date = models.DateTimeField(null=True,auto_now_add=False,auto_now=False,blank=True)
    total_hours = models.CharField(max_length=256,null=True,blank=True)
    user_obj = models.ForeignKey(User,related_name="uid",on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.user_obj.first_name + " " + str(self.date)

def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = instance.user_obj.first_name + "_" + "." + ext
    print(filename,"aaa")
    return os.path.join("training/%d-%m-%Y", filename)

class UserImages(TimeStampModel):
    user_obj = models.ForeignKey(User,related_name="user_image",on_delete=models.CASCADE,null=True,blank=True)
    image = models.FileField(upload_to="training/%Y/%m/%d", null=True,blank=True)

    def __str__(self):
        return self.user_obj.first_name

    class Meta:
        verbose_name_plural = "UserImages"


def user_directory_path(instance, filename):
    return instance.user.first_name + "/zips/"


class Attachment(models.Model):
    attachment = models.FileField(upload_to=user_directory_path,null=True,blank=True)
    export_dir = models.FileField(upload_to="exports",null=True,blank=True)
    user = models.ForeignKey(User,related_name="user_obj",on_delete=models.CASCADE,null=True)
    extracts = models.FileField(upload_to="extracts",null=True,blank=True)

@receiver(models.signals.post_delete, sender=Attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.attachment:
        if os.path.isfile(instance.attachment.path):
            os.remove(instance.attachment.path)
            # d = "media/"+ instance.user.first_name + "/extracts/"+ instance.attachment.name
            # shutil.rmtree(d)




@receiver(models.signals.post_delete, sender=UserImages)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# @receiver(models.signals.post_save, sender=UserImages)
# def auto_rename(sender, instance, **kwargs):
#     """
#     Deletes file from filesystem
#     when corresponding `MediaFile` object is deleted.
#     """
#     if instance.image:
#         ext = instance.image.name.split('.')[-1]
#         instance.image.name = instance.user_obj.first_name + "_" + "." + ext
#         instance.save()

class TrainingFile(TimeStampModel):
    dat_file = models.FileField(db_index=True, upload_to='models')

    def __str__(self):
        return self.dat_file.name