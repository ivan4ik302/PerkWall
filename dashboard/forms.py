from os import name
from django import forms
from django.forms.forms import Form
from django.forms.widgets import FileInput


class UserBioForm(forms.Form):
    bio = forms.CharField(max_length=210, required=True, widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control mb-2',
                                                                                      'id': 'bioInput', 'rows': '3',
                                                                                      'placeholder': 'Not set', 'aria-describedby': 'dashboardIndexUserInfoBioError'}))

class NewUserSubscriptionForm(forms.Form):
    pass

class UserSubscriptionForm(forms.Form):
    price = forms.CharField(required=True, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}))

    name = forms.CharField(max_length=21, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control',
                                                                        'id': 'nameInput', 'aria-describedby': 'nameError'}))

    description = forms.CharField(max_length=210, widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control',
                                                                               'id': 'descriptionInput', 'rows': '3',
                                                                               'aria-describedby': 'descriptionError'}))
    def clean_price(self):
        price = self.cleaned_data['price']
        try:
            int_price = int(price)
            if int_price == 0 or int_price < 0:
                self.add_error('price', 'Price must be greater than zero')

        except Exception:
            self.add_error('price', 'Price should be integer.')

        return price

class DeleteUserSubscriptionForm(forms.Form):
    pass

class UserProductForm(forms.Form):
    price = forms.CharField(required=True, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}))

    name =  forms.CharField(max_length=21, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control',
                                                                        'id': 'nameInput', 'aria-describedby': 'nameError'}))

    title = forms.CharField(max_length=210, widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control',
                                                                         'id': 'titleInput', 'rows': '3',
                                                                         'aria-describedby': 'titleError'}))

    body = forms.CharField(widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control invisibleInput',
                                                        'data-textarea-for-quill-id': 'editorContainer', 'aria-describedby': 'bodyError',
                                                        'rows': '3', 'readonly': True}))

    file = forms.FileField(required=False, widget=forms.FileInput(attrs={'type': 'file', 'class': 'form-control fileCustom',
                                                                         'aria-describedby': 'fileError', 'id': 'fileProductInput'}))

    is_file_change = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input invisibleInput checkboxDisable',
                                                                                          'data-checkbox-for-file-custom-id': 'fileProductInput'}))

    def clean_price(self):
        price = self.cleaned_data['price']
        try:
            int_price = int(price)
            if int_price <= 0:
                self.add_error('price', 'Price must be greater then zero')

        except Exception:
            self.add_error('price', 'Price should be integer.')

        return price

    def clean_body(self):
        body = self.cleaned_data['body']
        if body == '{\"ops\":[{"insert\":\"\\n\"}]}':
            self.add_error('body', 'This field is required.')

        return body

class DeleteUserProductForm(forms.Form):
    pass

class UserSubscriptionProductForm(forms.Form):
    subscription = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    name =  forms.CharField(max_length=21, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control',
                                                                        'id': 'nameInput', 'aria-describedby': 'nameError'}))

    title = forms.CharField(max_length=210, widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control',
                                                                         'id': 'titleInput', 'rows': '3',
                                                                         'aria-describedby': 'titleError'}))

    body = forms.CharField(widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control invisibleInput',
                                                        'data-textarea-for-quill-id': 'editorContainer', 'aria-describedby': 'bodyError',
                                                        'rows': '3', 'readonly': True}))

    file = forms.FileField(required=False, widget=forms.FileInput(attrs={'type': 'file', 'class': 'form-control fileCustom',
                                                                         'aria-describedby': 'fileError', 'id': 'fileSubscriptionProductInput'}))

    is_file_change = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input invisibleInput checkboxDisable',
                                                                                          'data-checkbox-for-file-custom-id': 'fileSubscriptionProductInput'}))

    def __init__(self, *args,**kwargs):
        subscription_choices = None
        if 'subscription_choices' in kwargs.keys():
            subscription_choices = kwargs.pop('subscription_choices')

        super(UserSubscriptionProductForm, self).__init__(*args, **kwargs)
        if subscription_choices is not None:
            self.fields['subscription'].choices = subscription_choices

    def clean_body(self):
        body = self.cleaned_data['body']
        if body == '{\"ops\":[{"insert\":\"\\n\"}]}':
            self.add_error('body', 'This field is required.')

        return body

class DeleteUserSubscriptionProductForm(forms.Form):
    pass

class UserPreviewForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control invisibleInput',
                                                        'data-textarea-for-quill-view-id': 'viewContainer','rows': '3', 
                                                        'readonly': True}))

