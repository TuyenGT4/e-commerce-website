from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from userauths.models import User

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

USER_TYPE = (
    ("Vendor", "Vendor"),
    ("Customer", "Customer"),
)

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder':'Full Name'}), required=True)
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder':'Mobile Number'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded' , 'placeholder':'Email Address'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded' , 'placeholder':'Password'}), validators=[validate_password], required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={ 'class': 'form-control rounded' , 'placeholder':'Confirm Password'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    user_type = forms.ChoiceField(choices=USER_TYPE, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = User
        fields = ['full_name', 'mobile', 'email', 'password1', 'password2', 'captcha', 'user_type']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use. Please choose a different one.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = self.data.get("password1")
        password_confirm = self.data.get("password2")

        if 'password2' in self._errors:
            del self._errors['password2']

        if password and password_confirm and password != password_confirm:
            self.add_error('password2', "The confirmed password does not match.")
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded' , 'name': "email", 'placeholder':'Email Address'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control rounded' , 'name': "password", 'placeholder':'Password'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ['email', 'password', 'captcha']
