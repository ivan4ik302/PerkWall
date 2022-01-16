from django.contrib import admin
from .models import Profile, UserSubscription, UserProduct, UserSubscriptionProduct, UserBillProduct, UserBillSubscription

admin.site.register(Profile)
admin.site.register(UserSubscription)
admin.site.register(UserProduct)
admin.site.register(UserSubscriptionProduct)
admin.site.register(UserBillProduct)
admin.site.register(UserBillSubscription)