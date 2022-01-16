from django.urls.base import reverse
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.http import Http404
from account.models import UserSubscription, UserProduct, UserSubscriptionProduct, UserBillProduct, UserBillSubscription
from perkwall.settings import ForeignIteamListView
from datetime import date, datetime
from django.core.paginator import Paginator
from . import forms

@require_GET
@login_required
def wall_main(request):
    user_name = request.GET.get('user_name', None)
    user = None
    bio_form = forms.BioForm()
    if user_name is not None:
        if user_name == request.user.username:
            return redirect (reverse('dashboard-main'))
        
        else:
            try:
                user = User.objects.get(username = user_name)

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

        products = ForeignIteamListView(products = UserProduct.objects.all().filter(user=user), bill_products=UserBillProduct.objects.all().filter(user=request.user), short=True)
        subscription_products = ForeignIteamListView(subscription_products = UserSubscriptionProduct.objects.all().filter(user=user), bill_subscriptions=UserBillSubscription.objects.all().filter(user=request.user), short=True)
        subscriptions = ForeignIteamListView(subscriptions = UserSubscription.objects.all().filter(user=user), bill_subscriptions=UserBillSubscription.objects.all().filter(user=request.user), short=True)
        bio_form.initial['bio'] = user.profile.bio
        return render(request, 'wall/index.html', context={'user': user, 'bio_form': bio_form, 'products': products, 'subscription_products': subscription_products, 'subscriptions': subscriptions})

    raise Http404

@require_GET
@login_required
def wall_view(request, kind):
    view_form = forms.ViewForm()
    name = None
    title = None
    look_file_link = False
    look_file_link_name = None
    look_file_link_url = None
    product_id = request.GET.get('product_id', None)
    subscription_product_id = request.GET.get('subscription_product_id', None)
    if (kind == 'product' and product_id is not None) or (kind == 'subscription-product' and subscription_product_id is not None):
        view_object = None
        if kind == 'product':
            try:
                view_object = UserProduct.objects.get(id=product_id)
                if view_object.user == request.user:
                    return redirect (reverse('dashboard-main'))

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

            try:
                UserBillProduct.objects.get(user=request.user, product=view_object)

            except (ObjectDoesNotExist):
                raise PermissionDenied()

        else:
            try:
                view_object = UserSubscriptionProduct.objects.get(id=subscription_product_id)
                if view_object.user == request.user:
                    return redirect (reverse('dashboard-main'))

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

            if view_object.subscription is not None:
                try:
                    bill_subscription = UserBillSubscription.objects.get(user=request.user, subscription=view_object.subscription)
                    if bill_subscription.expires < datetime.utcnow():
                        raise PermissionDenied()

                except (ObjectDoesNotExist):
                    raise PermissionDenied()

        if view_object.file:
            look_file_link = True
            look_file_link_name =  view_object.file.name
            ind_file_name_start = view_object.file.name.find('/')
            if ind_file_name_start != -1:
                look_file_link_name = view_object.file.name[ind_file_name_start + 1:]

            if len(look_file_link_name) > 21:
                look_file_link_name = look_file_link_name[:7] + '...' + look_file_link_name[-7:]

            look_file_link_url = view_object.file.url

        view_form.initial['body'] = view_object.body
        name = view_object.name
        title = view_object.title
        return render(request, 'wall/view.html', context={'view_form': view_form, 'name': name, 'title': title, 'look_file_link': look_file_link, 'look_file_link_name': look_file_link_name, 'look_file_link_url': look_file_link_url})
    
    raise Http404

@require_GET
@login_required
def wall_view_page(request, kind):
    page_number = request.GET.get('page_number', None)
    page_object = None
    view_object = None
    user_name = request.GET.get('user_name', None)
    user = None
    if page_number is not None and user_name is not None and (kind == 'product' or kind == 'subscription-product'):
        if user_name == request.user.username:
            return redirect (reverse('dashboard-main'))
        
        else:
            try:
                user = User.objects.get(username = user_name)

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

        if kind == 'product':
            view_object = ForeignIteamListView(products = UserProduct.objects.all().filter(user=user), bill_products=UserBillProduct.objects.all().filter(user=request.user))
        
        elif kind == 'subscription-product':
            view_object = ForeignIteamListView(subscription_products = UserSubscriptionProduct.objects.all().filter(user=user), bill_subscriptions=UserBillSubscription.objects.all().filter(user=request.user), short=True)
        
        if len(view_object) != 0:
            page_object = Paginator(view_object, 9).get_page(page_number)

        else:
            raise Http404()

        return render(request, 'wall/view-page.html', context={'user': user, 'page_object': page_object})

    raise Http404()

