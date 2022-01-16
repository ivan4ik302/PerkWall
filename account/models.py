from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from unidecode import unidecode
import time
import hashlib
import os

def custom_file_name(instance, filename):
    return os.path.join(f'{instance.user.username}#{instance.user.pk}', unidecode(filename))

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=210, blank=True)

    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.user:
            self.user.delete()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()
    name = models.CharField(max_length=21)
    description = models.TextField(max_length=210)

    def __str__(self):
        return f'{self.user.username}#{self.pk}'

    class Meta:
        ordering = ['-id']

class UserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()
    name = models.CharField(max_length=21)
    title = models.TextField(max_length=210)
    body = models.TextField()
    file = models.FileField(upload_to=custom_file_name, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}#{self.pk}'

    class Meta:
        ordering = ['-id']

class UserSubscriptionProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=21)
    title = models.TextField(max_length=210)
    body = models.TextField()
    file = models.FileField(upload_to=custom_file_name, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}#{self.pk}'

    class Meta:
        ordering = ['-id']

class UserBillProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(UserProduct, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}-product-{self.product.user.username}#{self.product.pk}'

class UserBillSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE)
    expires = models.DateTimeField()

    def __str__(self):
        return f'{self.user.username}-subscription-{self.subscription.user.username}#{self.subscription.pk}'