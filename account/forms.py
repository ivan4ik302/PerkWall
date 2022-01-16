from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    nickname = forms.CharField(validators=[ASCIIUsernameValidator()], required=True, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control',
                                                                                                                   'id': 'nicknameInput', 'aria-describedby': 'nicknameError'}))

    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'type': 'email', 'class': 'form-control',
                                                                          'id': 'emailInput', 'aria-describedby': 'emailError'}))

    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control',
                                                                                'id': 'passwordInput', 'aria-describedby': 'passwordError'}))

    password_confirm = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control',
                                                                                        'id': 'passwordConfirmInput', 'aria-describedby': 'passwordConfirmError'}))

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        try:
            users = User.objects.filter(username=nickname)
            if len(list(users)) != 0:
                self.add_error('nickname', 'User with this nickname already exists.')
        
        except Exception:
            self.add_error(None, '')

        return nickname

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            users = User.objects.filter(email=email)
            if len(list(users)) != 0:
                self.add_error('email', 'User with this email already exists.')

        except Exception:
            self.add_error(None, '')
            
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Password mismatch.')

class LoginForm(forms.Form):
    nickname = forms.CharField(required=True, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control',
                                                                            'id': 'nicknameInput', 'aria-describedby': 'nicknameError'}))

    password = forms.CharField(required=True, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control',
                                                                            'id': 'passwordInput', 'aria-describedby': 'passwordError'}))
