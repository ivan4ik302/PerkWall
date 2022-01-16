from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.conf import settings

from dashboard.views import dashboard_main
from . import forms

@require_http_methods(['GET', 'POST'])
def account_login(request):
    bound_form = forms.LoginForm()
    not_login_redirect = True if request.GET.get('next', False) else False
    if request.method == 'POST':
        not_login_redirect = False
        bound_form = forms.LoginForm(request.POST)
        use_auto_complete = False
        if request.user.is_authenticated:
            if bound_form.data['nickname'] == request.user.username and bound_form.data['password'] == settings.PASSWORD_PLUG:
                use_auto_complete = True
        
        if bound_form.is_valid() or use_auto_complete:
            try:
                user = None
                if use_auto_complete:
                    user = request.user

                else:
                    user = authenticate(request,
                                        username=bound_form.cleaned_data['nickname'],
                                        password=bound_form.cleaned_data['password'])
                                        
                    if user is not None:
                        login(request, user)

                if user is not None:
                    return redirect(request.GET.get('next', reverse('dashboard-main')))
                
                else:
                   bound_form.add_error('password', 'Invalid nickname or password.')

            except Exception:
                bound_form.add_error(None, '')
        
    else:
        if request.user.is_authenticated:
            bound_form.initial['nickname'] = request.user.username
            bound_form.initial['password'] = settings.PASSWORD_PLUG

    return render(request, 'account/login.html', context={'form': bound_form, 'not_login_redirect': not_login_redirect})

@require_http_methods(['GET', 'POST'])
def account_registration(request):
    bound_form = forms.RegistrationForm()
    if request.method == 'POST':
        bound_form = forms.RegistrationForm(request.POST)
        if bound_form.is_valid():
            try:
                user = User.objects.create_user(username=bound_form.cleaned_data['nickname'], email=bound_form.cleaned_data['email'], password=bound_form.cleaned_data['password'])
                user = authenticate(request,
                                    username=bound_form.cleaned_data['nickname'],
                                    email=bound_form.cleaned_data['email'],
                                    password=bound_form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    return redirect(reverse('dashboard-main'))

                else:
                    raise Exception()
            
            except Exception:
                bound_form.add_error(None, '')

    return render(request, 'account/registration.html', context={'form': bound_form})

@require_GET
def account_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect(reverse('account-login'))
