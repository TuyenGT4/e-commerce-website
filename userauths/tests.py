from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from userauths.models import User, Profile


class ProfileModelTestCase(TestCase):
    def test_profile_without_full_name_uses_user_full_name(self):
        user = User.objects.create_user(
            email='profile@example.com',
            password='StrongPass123!',
            username='profile',
            first_name='Nguyen',
            last_name='Hung',
        )

        profile = Profile.objects.create(user=user)

        self.assertEqual(profile.full_name, 'Nguyen Hung')

    def test_profile_without_full_name_falls_back_to_username(self):
        user = User.objects.create_user(
            email='profile-fallback@example.com',
            password='StrongPass123!',
            username='profilefallback',
        )

        profile = Profile.objects.create(user=user)

        self.assertEqual(profile.full_name, 'profilefallback')


class UserRegistrationParetoTestCase(TestCase):
    def setUp(self):
        # Khởi tạo Client (trình duyệt ảo) và cấu hình URL
        self.client = Client()
        self.signup_url = reverse('userauths:sign-up') 

    # 1. CASE 1: Đăng ký thành công (Happy Path)
    @patch('captcha.fields.ReCaptchaField.clean')
    def test_signup_happy_path(self, mock_captcha_clean):
        # Giả lập Captcha hợp lệ
        mock_captcha_clean.return_value = 'PASSED'
        
        form_data = {
            'full_name': 'Nguyen Van Hung',
            'mobile': '0987654321', 
            'email': 'testuser@gmail.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'user_type': 'Customer',
            'g-recaptcha-response': 'PASSED'
        }

        response = self.client.post(self.signup_url, data=form_data)

        # Trình duyệt phải được chuyển hướng (302) về trang chủ sau khi đăng ký thành công
        self.assertEqual(response.status_code, 302)
        
        # Kiểm tra Database: Phải có đúng 1 User và 1 Profile được tạo ra
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        
        # Kiểm tra dữ liệu lưu chuẩn xác
        user = User.objects.get(email='testuser@gmail.com')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.full_name, 'Nguyen Van Hung')
        self.assertEqual(profile.user_type, 'Customer')

    # 2. CASE 2: Bắt lỗi Email đã tồn tại (Data Integrity)
    @patch('captcha.fields.ReCaptchaField.clean')
    def test_signup_email_already_exists(self, mock_captcha_clean):
        mock_captcha_clean.return_value = 'PASSED'
        
        # TẠO SẴN 1 user có email là exist@gmail.com trong Database ảo
        User.objects.create_user(email='exist@gmail.com', password='OldPassword123!', username='exist')

        form_data = {
            'full_name': 'Hacker X',
            'mobile': '0111222333',
            'email': 'exist@gmail.com', # CỐ TÌNH DÙNG LẠI EMAIL NÀY
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'user_type': 'Customer',
            'g-recaptcha-response': 'PASSED'
        }

        response = self.client.post(self.signup_url, data=form_data)

        # Server phải chặn lại và trả về chính trang form hiện tại (200)
        self.assertEqual(response.status_code, 200)
        
        # Database KHÔNG ĐƯỢC PHÉP tạo thêm user mới (Vẫn chỉ có 1 user cũ)
        self.assertEqual(User.objects.count(), 1)
        
        # Form phải bắn ra lỗi ở trường 'email'
        form = response.context.get('form')
        self.assertIn('email', form.errors)

    # 3. CORE CASE 3: Bắt lỗi Mật khẩu không khớp (Business Logic)
    @patch('captcha.fields.ReCaptchaField.clean')
    def test_signup_password_mismatch(self, mock_captcha_clean):
        mock_captcha_clean.return_value = 'PASSED'
        
        form_data = {
            'full_name': 'Nguyen Van Hung',
            'mobile': '0987654321',
            'email': 'testmismatch@gmail.com',
            'password1': 'StrongPass123!',
            'password2': 'WrongPass000!', # CỐ TÌNH NHẬP SAI XÁC NHẬN
            'user_type': 'Customer',
            'g-recaptcha-response': 'PASSED'
        }

        response = self.client.post(self.signup_url, data=form_data)

        # Bị chặn lại ở trang form
        self.assertEqual(response.status_code, 200)
        
        # Database không có User nào được tạo ra
        self.assertEqual(User.objects.count(), 0)
        
        # Form phải bắn ra lỗi ở trường 'password2' (Xác nhận mật khẩu)
        form = response.context.get('form')
        self.assertIn('password2', form.errors)

class UserLoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('userauths:sign-in') # Đảm bảo url name của bạn đúng
        self.index_url = reverse('store:index')       # Giả định url name trang chủ
        
        # Tạo sẵn một User chuẩn trong Database ảo để test login
        self.test_user = User.objects.create_user(
            email='testlogin@gmail.com',
            password='CorrectPassword123!',
            username='testlogin'
        )

    # 1. CORE CASE 1: Đăng nhập thành công (Happy Path)
    @patch('captcha.fields.ReCaptchaField.clean')
    def test_login_successful(self, mock_captcha_clean):
        mock_captcha_clean.return_value = 'PASSED' # Giả lập vượt qua Captcha
        
        form_data = {
            'email': 'testlogin@gmail.com',
            'password': 'CorrectPassword123!',
            'g-recaptcha-response': 'PASSED'
        }

        response = self.client.post(self.login_url, data=form_data)

        # Trình duyệt chuyển hướng (302) về trang chủ
        self.assertEqual(response.status_code, 302)
        # Xác minh Session đã lưu ID của user (chứng tỏ đã đăng nhập)
        self.assertEqual(str(self.client.session['_auth_user_id']), str(self.test_user.id))

    # 2. CORE CASE 2: Sai mật khẩu / Sai Email
    @patch('captcha.fields.ReCaptchaField.clean')
    def test_login_wrong_credentials(self, mock_captcha_clean):
        mock_captcha_clean.return_value = 'PASSED'
        
        form_data = {
            'email': 'testlogin@gmail.com',
            'password': 'WrongPassword!!!', # Cố tình nhập sai pass
            'g-recaptcha-response': 'PASSED'
        }

        response = self.client.post(self.login_url, data=form_data)

        # Trả về lại trang đăng nhập (200) vì có lỗi
        self.assertEqual(response.status_code, 200)
        # Đảm bảo không có ai được lưu vào session (chưa đăng nhập)
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # Kiểm tra Message hiển thị lỗi chuẩn bảo mật
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'Email or password is incorrect')

    # 3. CORE CASE 3: Không tick Captcha
    def test_login_missing_captcha(self):
        # Không dùng @patch để giả lập, để form tự động bắt lỗi thiếu Captcha
        form_data = {
            'email': 'testlogin@gmail.com',
            'password': 'CorrectPassword123!',
            # Cố tình không gửi 'g-recaptcha-response'
        }

        response = self.client.post(self.login_url, data=form_data)

        # Trả về lại trang đăng nhập (200)
        self.assertEqual(response.status_code, 200)
        # Chưa đăng nhập
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # Đảm bảo có lỗi báo ra ngoài Message liên quan đến Captcha
        messages = list(response.context['messages'])
        self.assertTrue(any('Captcha verification failed' in str(m) for m in messages))

    # 4. CORE CASE 4: Đã đăng nhập rồi nhưng cố tình vào lại trang Login
    def test_login_already_authenticated(self):
        # Ép trình duyệt ảo (client) đăng nhập luôn từ đầu
        self.client.force_login(self.test_user)

        # Cố tình truy cập trang đăng nhập (bằng phương thức GET)
        response = self.client.get(self.login_url)

        # Hệ thống phải lập tức đẩy văng ra trang chủ (302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.index_url)
