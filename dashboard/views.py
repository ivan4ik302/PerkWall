from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET,  require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from account.models import UserSubscription, UserProduct, UserSubscriptionProduct, UserBillProduct, UserBillSubscription
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.core.paginator import Paginator
from perkwall.settings import SelfIteamListView
from perkwall.settings import ForeignIteamListView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from . import forms
import json
from django.db.models import Q

@require_http_methods(['GET', 'POST'])
@login_required
def dashboard_main(request):
    user_bio_form = forms.UserBioForm()
    if request.method == 'POST':
        if request.POST.get('form_type') == 'userBioForm':
            user_bio_form = forms.UserBioForm(request.POST)
            if user_bio_form.is_valid():
                try:
                    if request.user.profile.bio != user_bio_form.cleaned_data['bio']:
                        request.user.profile.bio = user_bio_form.cleaned_data['bio']
                        request.user.save()

                except Exception:
                    user_bio_form.add_error(None, '')

    user_bio_form.initial['bio'] = request.user.profile.bio
    user_products = SelfIteamListView(products=UserProduct.objects.all().filter(user=request.user), short=True)
    user_subscription_products = SelfIteamListView(subscription_products=UserSubscriptionProduct.objects.all().filter(user=request.user), short=True)
    return render(request, 'dashboard/index.html', context={'user_bio_form': user_bio_form, 'user_products': user_products, 'user_subscription_products': user_subscription_products})

@require_http_methods(['GET', 'POST'])
@login_required
def dashboard_account(request):
    new_user_subscription_form = forms.NewUserSubscriptionForm()
    if request.method == 'POST':
        if request.POST.get('form_type') == 'newUserSubscriptionForm':
            new_user_subscription_form = forms.NewUserSubscriptionForm(request.POST)
            if new_user_subscription_form.is_valid():
                try:
                    if len(UserSubscription.objects.all().filter(user=request.user)) < settings.MAX_USER_SUBSCRIPTIONS:
                        return redirect(f'{reverse("dashboard-user-subscription")}?action=add')

                    else:
                        new_user_subscription_form.add_error(None, 'You cannot have more than three subscriptions.')

                except Exception:
                    new_user_subscription_form.add_error(None, 'Something went wrong, try again!')

    user_subscriptions = SelfIteamListView(subscriptions=UserSubscription.objects.all().filter(user=request.user), short=True)
    products = ForeignIteamListView(bill_products=UserBillProduct.objects.all().filter(user=request.user), short=True)
    subscriptions = ForeignIteamListView(bill_subscriptions=UserBillSubscription.objects.all().filter(user=request.user), short=True)
    return render(request, 'dashboard/account.html', context={'new_user_subscription_form': new_user_subscription_form, 'user_subscriptions': user_subscriptions, 'products': products, 'subscriptions': subscriptions})

@require_http_methods(['GET', 'POST'])
@login_required
def dashboard_user_subscription(request):
    action = request.GET.get('action', None)
    user_subscription_id = request.GET.get('user_subscription_id', None)
    user_subscription_delete_button = False
    user_subscription_form = forms.UserSubscriptionForm()
    delete_user_subscription_form = forms.DeleteUserSubscriptionForm()
    if action is not None and action == 'add':
        if len(UserSubscription.objects.all().filter(user=request.user)) >= settings.MAX_USER_SUBSCRIPTIONS:
            return redirect(reverse('dashboard-account'))
            
        if request.method == 'POST':
            if request.POST.get('form_type') ==  'userSubscriptionForm':
                user_subscription_form = forms.UserSubscriptionForm(request.POST)
                if user_subscription_form.is_valid():
                    try:
                        UserSubscription.objects.create(user = request.user, price = int(user_subscription_form.cleaned_data['price']), name = user_subscription_form.cleaned_data['name'], description = user_subscription_form.cleaned_data['description'])
                        return redirect(reverse('dashboard-account'))

                    except Exception:
                        user_subscription_form.add_error(None, '' )

    elif action is not None and action == 'change' and user_subscription_id is not None:
        user_subscription_delete_button = True
        user_subscription = None
        try:
            user_subscription = UserSubscription.objects.get(user = request.user, id = user_subscription_id)

        except (ObjectDoesNotExist, ValueError):
            raise Http404()

        if request.method == 'POST':
            if request.POST.get('form_type') == 'userSubscriptionForm':
                user_subscription_form = forms.UserSubscriptionForm(request.POST)
                if user_subscription_form.is_valid():
                    try:
                        user_subscription.price = user_subscription_form.cleaned_data['price']
                        user_subscription.name = user_subscription_form.cleaned_data['name']
                        user_subscription.description = user_subscription_form.cleaned_data['description']
                        user_subscription.save()
                        return redirect(reverse('dashboard-account'))

                    except Exception:
                        user_subscription_form.add_error(None, '' )

            elif request.POST.get('form_type') ==  'deleteUserSubscriptionForm':
                delete_user_subscription_form = forms.DeleteUserSubscriptionForm(request.POST)
                user_subscription_form.initial['price'] = user_subscription.price
                user_subscription_form.initial['name'] = user_subscription.name
                user_subscription_form.initial['description'] = user_subscription.description
                if delete_user_subscription_form.is_valid():
                    try:
                        user_subscription.delete()
                        return redirect(reverse('dashboard-account'))

                    except Exception:
                        delete_user_subscription_form.add_error(None, '')

        else:
            user_subscription_form.initial['price'] = user_subscription.price
            user_subscription_form.initial['name'] = user_subscription.name
            user_subscription_form.initial['description'] = user_subscription.description

    else:
        raise Http404()

    return render(request, 'dashboard/user-subscription.html', context={'user_subscription_form': user_subscription_form, 'delete_user_subscription_form': delete_user_subscription_form, 'user_subscription_delete_button': user_subscription_delete_button})

@require_http_methods(['GET', 'POST'])
@login_required
def dashboard_user_product(request):
    action = request.GET.get('action', None)
    user_product_id = request.GET.get('user_product_id', None)
    user_product_form = forms.UserProductForm()
    user_product_delete_button = False
    user_product_look_file_link = False
    user_product_look_file_link_name = None
    user_product_look_file_link_url = None
    delete_user_product_form = forms.DeleteUserProductForm()
    if action is not None and action == 'add':
        if request.method == 'POST':
            if 'X-Requested-With' in request.headers and request.headers['X-Requested-With'] == 'XMLHttpRequest':
                user_product_form = forms.UserProductForm(request.POST, request.FILES)
                if user_product_form.is_valid() and (('file' in request.POST.keys()) or ('file' not in request.POST.keys() and 'file' in request.FILES.keys())):
                    try:
                        UserProduct.objects.create(user = request.user, price = int(user_product_form.cleaned_data['price']), name = user_product_form.cleaned_data['name'], title = user_product_form.cleaned_data['title'], body = user_product_form.cleaned_data['body'], file = user_product_form.cleaned_data['file'])
                        return JsonResponse({'redirect': reverse('dashboard-main'), 'errors': None})

                    except Exception:
                        user_product_form.add_error(None,'')
                
                return JsonResponse({'redirect': None, 'errors': json.loads(user_product_form.errors.as_json())})

    elif action is not None and action == 'change' and user_product_id is not None:
        user_product_delete_button = True
        user_product = None
        try:
            user_product = UserProduct.objects.get(user = request.user, id = user_product_id)

        except (ObjectDoesNotExist, ValueError):
            raise Http404()

        if user_product.file:
            user_product_look_file_link = True
            user_product_look_file_link_name =  user_product.file.name
            ind_file_name_start = user_product.file.name.find('/')
            if ind_file_name_start != -1:
                user_product_look_file_link_name = user_product.file.name[ind_file_name_start + 1:]

            if len(user_product_look_file_link_name) > 21:
                user_product_look_file_link_name = user_product_look_file_link_name[:7] + '...' + user_product_look_file_link_name[-7:]

            user_product_look_file_link_url = user_product.file.url

        if request.method == 'POST':
            if 'X-Requested-With' in request.headers and request.headers['X-Requested-With'] == 'XMLHttpRequest':
                user_product_form = forms.UserProductForm(request.POST, request.FILES)
                if user_product_form.is_valid() and (('file' in request.POST.keys()) or ('file' not in request.POST.keys() and 'file' in request.FILES.keys())):
                    try:
                        user_product.price = int(user_product_form.cleaned_data['price'])
                        user_product.name = user_product_form.cleaned_data['name']
                        user_product.title = user_product_form.cleaned_data['title']
                        user_product.body = user_product_form.cleaned_data['body']
                        if user_product_form.cleaned_data['is_file_change']:
                            user_product.file = user_product_form.cleaned_data['file']

                        user_product.save()
                        return JsonResponse({'redirect': reverse('dashboard-main'), 'errors': None})

                    except Exception:
                        user_product_form.add_error(None,'')

                return JsonResponse({'redirect': None, 'errors': json.loads(user_product_form.errors.as_json())})

            elif request.POST.get('form_type') == 'deleteUserProductForm':
                delete_user_product_form = forms.DeleteUserProductForm(request.POST)
                user_product_form.initial['price'] = user_product.price
                user_product_form.initial['name'] = user_product.name
                user_product_form.initial['title'] = user_product.title
                user_product_form.initial['body'] = user_product.body
                if delete_user_product_form.is_valid():
                    try:
                        user_product.delete()
                        return redirect(reverse('dashboard-main'))

                    except Exception:
                        delete_user_product_form.add_error(None, '')

        else:
            user_product_form.initial['price'] = user_product.price
            user_product_form.initial['name'] = user_product.name
            user_product_form.initial['title'] = user_product.title
            user_product_form.initial['body'] = user_product.body

    else:
        raise Http404()

    return render(request, 'dashboard/user-product.html', context={'user_product_form': user_product_form, 'delete_user_product_form': delete_user_product_form, 'user_product_delete_button': user_product_delete_button, 'user_product_look_file_link': user_product_look_file_link, 'user_product_look_file_link_name': user_product_look_file_link_name, 'user_product_look_file_link_url': user_product_look_file_link_url})

@require_http_methods(['GET', 'POST'])
@login_required
def dashboard_user_subscription_product(request):
    action = request.GET.get('action', None)
    user_subscription_product_id = request.GET.get('user_subscription_product_id', None)
    subscription_choices = [(None,'Free')]
    user_subscriptions = UserSubscription.objects.all().filter(user=request.user)
    for user_subscription in user_subscriptions:
        subscription_choices.append((str(user_subscription.id), f'{user_subscription.price}$ - {user_subscription.name}'))

    user_subscription_product_form = forms.UserSubscriptionProductForm(subscription_choices = subscription_choices)
    user_subscription_product_delete_button = False
    user_subscription_product_look_file_link = False
    user_subscription_product_look_file_link_name = None
    user_subscription_product_look_file_link_url = None
    delete_user_subscription_product_form = forms.DeleteUserSubscriptionProductForm()
    if action is not None and action == 'add':
        if request.method == 'POST':
            if 'X-Requested-With' in request.headers and request.headers['X-Requested-With'] == 'XMLHttpRequest':
                user_subscription_product_form = forms.UserSubscriptionProductForm(request.POST, request.FILES, subscription_choices = subscription_choices)
                if user_subscription_product_form.is_valid() and (('file' in request.POST.keys()) or ('file' not in request.POST.keys() and 'file' in request.FILES.keys())):
                    try:
                        user_subscription = None
                        if (user_subscription_product_form.cleaned_data['subscription']):
                            user_subscription = UserSubscription.objects.get(user=request.user, id = int(user_subscription_product_form.cleaned_data['subscription']))

                        UserSubscriptionProduct.objects.create(user = request.user, subscription = user_subscription, name = user_subscription_product_form.cleaned_data['name'], title = user_subscription_product_form.cleaned_data['title'], body = user_subscription_product_form.cleaned_data['body'], file = user_subscription_product_form.cleaned_data['file'])
                        return JsonResponse({'redirect': reverse('dashboard-main'), 'errors': None})

                    except Exception:
                        user_subscription_product_form.add_error(None,'')
                    
                return JsonResponse({'redirect': None, 'errors': json.loads(user_subscription_product_form.errors.as_json())})

    elif action is not None and action == 'change' and user_subscription_product_id is not None:
        user_subscription_product_delete_button = True
        user_subscription_product = None
        try:
            user_subscription_product = UserSubscriptionProduct.objects.get(user = request.user, id = user_subscription_product_id)

        except (ObjectDoesNotExist, ValueError):
            raise Http404()

        if user_subscription_product.file:
            user_subscription_product_look_file_link = True
            user_subscription_product_look_file_link_name =  user_subscription_product.file.name
            ind_file_name_start = user_subscription_product.file.name.find('/')
            if ind_file_name_start != -1:
                user_subscription_product_look_file_link_name = user_subscription_product.file.name[ind_file_name_start + 1:]

            if len(user_subscription_product_look_file_link_name) > 21:
                user_subscription_product_look_file_link_name = user_subscription_product_look_file_link_name[:7] + '...' + user_subscription_product_look_file_link_name[-7:]

            user_subscription_product_look_file_link_url = user_subscription_product.file.url

        if request.method == 'POST':
            if 'X-Requested-With' in request.headers and request.headers['X-Requested-With'] == 'XMLHttpRequest':
                user_subscription_product_form = forms.UserSubscriptionProductForm(request.POST, request.FILES, subscription_choices = subscription_choices)
                if user_subscription_product_form.is_valid() and (('file' in request.POST.keys()) or ('file' not in request.POST.keys() and 'file' in request.FILES.keys())):
                    try:
                        user_subscription = None
                        if (user_subscription_product_form.cleaned_data['subscription']):
                            user_subscription = UserSubscription.objects.get(user=request.user, id = int(user_subscription_product_form.cleaned_data['subscription']))

                        user_subscription_product.subscription = user_subscription
                        user_subscription_product.name = user_subscription_product_form.cleaned_data['name']
                        user_subscription_product.title = user_subscription_product_form.cleaned_data['title']
                        user_subscription_product.body = user_subscription_product_form.cleaned_data['body']
                        if user_subscription_product_form.cleaned_data['is_file_change']:
                            user_subscription_product.file = user_subscription_product_form.cleaned_data['file']

                        user_subscription_product.save()
                        return JsonResponse({'redirect': reverse('dashboard-main'), 'errors': None})

                    except Exception:
                        user_subscription_product_form.add_error(None,'')

                return JsonResponse({'redirect': None, 'errors': json.loads(user_subscription_product_form.errors.as_json())})

            elif request.POST.get('form_type') == 'deleteUserSubscriptionProductForm':
                delete_user_subscription_product_form = forms.DeleteUserSubscriptionProductForm(request.POST)
                if user_subscription_product.subscription is None:
                    user_subscription_product_form.initial['subscription'] = user_subscription_product.subscription

                else:
                    user_subscription_product_form.initial['subscription'] = user_subscription_product.subscription.id

                user_subscription_product_form.initial['name'] = user_subscription_product.name
                user_subscription_product_form.initial['title'] = user_subscription_product.title
                user_subscription_product_form.initial['body'] = user_subscription_product.body
                if delete_user_subscription_product_form.is_valid():
                    try:
                        user_subscription_product.delete()
                        return redirect(reverse('dashboard-main'))

                    except Exception:
                         delete_user_subscription_product_form.add_error(None, '')

        else:
            if user_subscription_product.subscription is None:
                user_subscription_product_form.initial['subscription'] = user_subscription_product.subscription

            else:
                user_subscription_product_form.initial['subscription'] = user_subscription_product.subscription.id 

            user_subscription_product_form.initial['name'] = user_subscription_product.name
            user_subscription_product_form.initial['title'] = user_subscription_product.title
            user_subscription_product_form.initial['body'] = user_subscription_product.body

    else:
        raise Http404()

    return render(request, 'dashboard/user-subscription-product.html', context={'user_subscription_product_form': user_subscription_product_form, 'delete_user_subscription_product_form': delete_user_subscription_product_form, 'user_subscription_product_delete_button': user_subscription_product_delete_button, 'user_subscription_product_look_file_link': user_subscription_product_look_file_link, 'user_subscription_product_look_file_link_name': user_subscription_product_look_file_link_name, 'user_subscription_product_look_file_link_url': user_subscription_product_look_file_link_url})

@require_GET
@login_required
def dashboard_user_preview(request, kind):
    user_preview_form = forms.UserPreviewForm()
    name = None
    title = None
    look_file_link = False
    look_file_link_name = None
    look_file_link_url = None
    user_product_id = request.GET.get('user_product_id', None)
    user_subscription_product_id = request.GET.get('user_subscription_product_id', None)
    if (kind == 'product' and user_product_id is not None) or (kind == 'subscription-product' and user_subscription_product_id is not None):
        view_object = None
        if kind == 'product':
            try:
                view_object = UserProduct.objects.get(user = request.user, id = user_product_id)

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

        else:
            try:
                view_object = UserSubscriptionProduct.objects.get(user = request.user, id = user_subscription_product_id)

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

        if view_object.file:
                look_file_link = True
                look_file_link_name =  view_object.file.name
                ind_file_name_start = view_object.file.name.find('/')
                if ind_file_name_start != -1:
                    look_file_link_name = view_object.file.name[ind_file_name_start + 1:]

                if len(look_file_link_name) > 21:
                    look_file_link_name = look_file_link_name[:7] + '...' + look_file_link_name[-7:]

                look_file_link_url = view_object.file.url

        user_preview_form.initial['body'] = view_object.body
        name = view_object.name
        title = view_object.title
        return render(request, 'dashboard/user-preview.html', context={'user_preview_form': user_preview_form, 'name': name, 'title': title, 'look_file_link': look_file_link, 'look_file_link_name': look_file_link_name, 'look_file_link_url': look_file_link_url})

    raise Http404()

@require_GET
@login_required
def dashboard_user_view_page(request, kind):
    page_number = request.GET.get('page_number', None)
    page_object = None
    view_object = None
    if page_number is not None and (kind == 'product' or kind == 'subscription-product'):
        if kind == 'product':
            view_object = SelfIteamListView(products = UserProduct.objects.all().filter(user=request.user))
        
        elif kind == 'subscription-product':
            view_object = SelfIteamListView(subscription_products = UserSubscriptionProduct.objects.all().filter(user=request.user))
        
        if len(view_object) != 0:
            page_object = Paginator(view_object, 9).get_page(page_number)

        else:
            raise Http404()

        return render(request, 'dashboard/user-view-page.html', context={'page_object': page_object})

    raise Http404()

@require_GET
@login_required
def dashboard_view_page(request, kind):
    page_number = request.GET.get('page_number', None)
    page_object = None
    view_object = None
    if page_number is not None and (kind == 'product' or kind == 'subscription'):
        if kind == 'product':
            view_object = ForeignIteamListView(bill_products=UserBillProduct.objects.all().filter(user=request.user))
        
        elif kind == 'subscription':
            view_object = ForeignIteamListView(bill_subscriptions=UserBillSubscription.objects.all().filter(user=request.user), short=True)
        
        if len(view_object) != 0:
            page_object = Paginator(view_object, 9).get_page(page_number)

        else:
            raise Http404()

        return render(request, 'dashboard/view-page.html', context={'page_object': page_object})

    raise Http404()

@require_GET
@login_required
def dashboard_users_list(request):
    users_list_form = forms.UsersListForm()
    users_list_form.initial['page_number'] = '1'
    return render(request, 'dashboard/users-list.html', context={'users_list_form': users_list_form})

@require_POST
@login_required
@csrf_exempt
def dashboard_users_list_get(request):
    request_body = json.loads(request.body)
    if request_body["user_name"] != '':
        fit_users = User.objects.all().filter(username__regex=rf'\b{request_body["user_name"]}').filter(~Q(username=request.user.username))

    else:
        fit_users = []

    page_object = Paginator(fit_users, 9).get_page(request_body['page_number'])
    response_body = {'users': []}
    for user in page_object:
        response_body['users'].append({'user_name': user.username, 'users_url': f'{reverse("wall-main")}?user_name={user.username}'})

    response_body['has_previous'] = page_object.has_previous()
    if page_object.has_previous():
        response_body['previous_page_number'] = page_object.previous_page_number()

    else:
        response_body['previous_page_number'] = None

    response_body['has_next'] = page_object.has_next()
    if page_object.has_next():
        response_body['next_page_number'] = page_object.next_page_number()

    else:
        response_body['next_page_number'] = None

    response_body['page_current_number'] = page_object.number
    response_body['page_number'] = page_object.paginator.num_pages

    return JsonResponse(response_body)