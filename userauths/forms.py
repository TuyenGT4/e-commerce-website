from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

from userauths.models import User

USER_TYPE = (
    ("Vendor", "Người bán"),
    ("Customer", "Khách hàng"),
)

# Validator số điện thoại Việt Nam
phone_validator = RegexValidator(
    regex=r'^(0[3|5|7|8|9])+([0-9]{8})$',
    message="Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại Việt Nam (VD: 0912345678)"
)


class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label="Họ và tên",
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'placeholder': 'Nguyễn Văn A'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng nhập họ và tên.'
        }
    )
    mobile = forms.CharField(
        label="Số điện thoại",
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'placeholder': '0912345678'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng nhập số điện thoại.'
        }
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'placeholder': 'example@email.com'
        }),
        required=True,
        error_messages={
            'required': 'Vui lòng nhập địa chỉ email.',
            'invalid': 'Địa chỉ email không hợp lệ.'
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
            'required': 'Vui lòng nhập mật khẩu.'
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
            'required': 'Vui lòng xác nhận mật khẩu.'
        }
    )
    user_type = forms.ChoiceField(
        label="Loại tài khoản",
        choices=USER_TYPE,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            'required': 'Vui lòng chọn loại tài khoản.',
            'invalid_choice': 'Loại tài khoản không hợp lệ.'
        }
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        error_messages={
            'required': 'Vui lòng xác minh captcha.'
        }
    )

    class Meta:
        model = User
        fields = ['full_name', 'mobile', 'email', 'password1', 'password2', 'user_type', 'captcha']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được đăng ký. Vui lòng dùng email khác.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Mật khẩu xác nhận không khớp. Vui lòng kiểm tra lại.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded',
            'name': 'email',
            'placeholder': 'example@email.com'
        }),
        required=True,  # Fix: required=False là không hợp lý cho login
        error_messages={
            'required': 'Vui lòng nhập địa chỉ email.',
            'invalid': 'Địa chỉ email không hợp lệ.'
        }
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded',
            'name': 'password',
            'placeholder': 'Nhập mật khẩu'
        }),
        required=True,  # Fix: required=False là không hợp lý cho login
        error_messages={
            'required': 'Vui lòng nhập mật khẩu.'
        }
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        error_messages={
            'required': 'Vui lòng xác minh captcha.'
        }
    )