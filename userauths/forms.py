from django import forms
from django.contrib.auth.forms import UserCreationForm

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

from userauths.models import User

USER_TYPE = (
    ("Vendor", "Nhà bán hàng"),
    ("Customer", "Khách hàng"),
)


class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label="Họ và tên",
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'placeholder': 'Nhập họ và tên'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng nhập họ và tên'
        }
    )
    mobile = forms.CharField(
        label="Số điện thoại",
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'placeholder': 'Nhập số điện thoại'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng nhập số điện thoại'
        }
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'placeholder': 'Nhập địa chỉ email'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng nhập địa chỉ email',
            'invalid': 'Địa chỉ email không hợp lệ'
        }
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded',
            'placeholder': 'Nhập mật khẩu'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng nhập mật khẩu'
        }
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded',
            'placeholder': 'Nhập lại mật khẩu'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng xác nhận mật khẩu'
        }
    )
    user_type = forms.ChoiceField(
        label="Loại tài khoản",
        choices=USER_TYPE,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        error_messages={
            'required': 'Vui lòng xác minh captcha'
        }
    )

    class Meta:
        model = User
        fields = [
            'full_name', 'mobile', 'email',
            'password1', 'password2',
            'user_type', 'captcha'
        ]

    def clean_password2(self):
        """Kiểm tra 2 mật khẩu có khớp nhau không"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Mật khẩu xác nhận không khớp')
        return password2

    def clean_email(self):
        """Kiểm tra email đã tồn tại chưa"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng')
        return email

    def clean_mobile(self):
        """Kiểm tra số điện thoại hợp lệ"""
        mobile = self.cleaned_data.get('mobile')
        if not mobile.isdigit():
            raise forms.ValidationError('Số điện thoại chỉ được chứa chữ số')
        if len(mobile) < 10 or len(mobile) > 11:
            raise forms.ValidationError('Số điện thoại phải có 10-11 chữ số')
        return mobile


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'name': 'email',
            'placeholder': 'Nhập địa chỉ email'
        }),
        required=False,
        error_messages={
            'invalid': 'Địa chỉ email không hợp lệ'
        }
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded',
            'name': 'password',
            'placeholder': 'Nhập mật khẩu'
        }),
        required=False
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        error_messages={
            'required': 'Vui lòng xác minh captcha'
        }
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'captcha']