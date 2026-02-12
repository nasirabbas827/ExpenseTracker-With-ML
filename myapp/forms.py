from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Category, Income, Expense


# ==========================================
# USER REGISTRATION FORM
# ==========================================
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })


# ==========================================
# LOGIN FORM
# ==========================================
class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

        self.fields['password'].widget = forms.PasswordInput(
            attrs=self.fields['password'].widget.attrs
        )


# ==========================================
# PROFILE FORM
# ==========================================
class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            'full_name',
            'email',
            'gender',
            'date_of_birth',
            'age',
            'phone_number',
            'address',
            'profile_picture',
        ]

        widgets = {
            'full_name': forms.TextInput(),
            'email': forms.EmailInput(),
            'gender': forms.Select(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'age': forms.NumberInput(attrs={'min': 0}),
            'phone_number': forms.TextInput(attrs={'pattern': '[0-9]*'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'profile_picture': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })


# ==========================================
# CATEGORY FORM
# ==========================================
class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter category name'
        })


# ==========================================
# INCOME FORM
# ==========================================
class IncomeForm(forms.ModelForm):

    class Meta:
        model = Income
        fields = ['amount', 'source', 'date', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'source': forms.TextInput(),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })


# ==========================================
# EXPENSE FORM
# ==========================================
class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'category': forms.Select(),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })


