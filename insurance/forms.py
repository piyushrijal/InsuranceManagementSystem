from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from . import models


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = 'Your username or password is incorrect. Please try again.'


class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class CategoryForm(forms.ModelForm):
    category_name = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={'class': 'text-field w-40 p-1', 'placeholder': 'Category Name'}))

    class Meta:
        model = models.Category
        fields = ['category_name']


class PolicyForm(forms.ModelForm):
    category = forms.ModelChoiceField(label="", queryset=models.Category.objects.all(), empty_label="Category Name",
                                      widget=forms.Select(attrs={'class': 'text-field w-100 py-2'}),
                                      to_field_name="id")
    policy_name = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={'class': 'text-field w-100 p-1', 'placeholder': 'Policy Name'}))
    sum_assurance = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={'class': 'text-field w-100 p-1', 'placeholder': 'Sum Assurance'}))
    premium = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={'class': 'text-field w-100 p-1', 'placeholder': 'Premium'}))
    tenure = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={'class': 'text-field w-100 p-1', 'placeholder': 'Tenure'}))

    class Meta:
        model = models.Policy
        fields = ['policy_name', 'sum_assurance', 'premium', 'tenure']


class QuestionForm(forms.ModelForm):
    description = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={'class': 'text-field w-100 p-1', 'placeholder': 'Ask Question'}))

    class Meta:
        model = models.Question
        fields = ['description']

    def clean_admin_comment(self):
        admin_comment = self.cleaned_data.get('admin_comment')
        if not admin_comment:
            raise forms.ValidationError("Admin comment cannot be empty.")
        return admin_comment
