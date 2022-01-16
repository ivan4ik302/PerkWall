from django import forms

class BioForm(forms.Form):
    bio = forms.CharField(widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control mb-2',
                                                        'id': 'bioInput', 'rows': '3',
                                                        'placeholder': 'Not set', 'aria-describedby': 'dashboardIndexUserInfoBioError',
                                                        'readonly': True}))

class ViewForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control invisibleInput',
                                                        'data-textarea-for-quill-view-id': 'viewContainer','rows': '3', 
                                                        'readonly': True}))