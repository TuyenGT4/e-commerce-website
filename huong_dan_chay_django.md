# Hướng Dẫn Chi Tiết Chạy Dự Án Django

Techstack: Bootstrap(FE) + Python_Django(BE) + Postgresql(DB)

## Bước 1: Cài Đặt Các Phụ Thuộc

Trước khi tiến hành, hãy đảm bảo bạn đã cài Python và `pip` (trình quản lý gói của Python) trên hệ thống. Bạn cũng cần gói tạo môi trường ảo.

1. **Kiểm tra cài đặt Python:**
   Mở terminal hoặc command prompt và gõ:

   ```bash
   python --version
   ```

   Nếu Python chưa được cài, hãy tải và cài đặt từ [python.org](https://www.python.org/downloads/).

2. **Cài đặt `virtualenv` (nếu chưa có):**
   Nếu bạn chưa có `virtualenv`, hãy cài đặt bằng lệnh:

   ```bash
   pip install virtualenv
   ```

---

## Bước 2: Giải Nén File Zip

1. Tải file về máy nếu chưa có.
2. Điều hướng đến thư mục chứa file zip vừa tải.
3. Nhấp chuột phải vào file zip và chọn **Extract Here** hoặc dùng công cụ như 7-Zip, WinRAR để giải nén vào thư mục

Sau đó, bạn sẽ thấy các file của dự án Django trong thư mục `e-commerce website`.

---

## Bước 3: Điều Hướng Đến Thư Mục Dự Án

Dùng terminal hoặc command prompt, chuyển thư mục làm việc sang thư mục `e-commerce website`:

```bash
cd e-commerce website
```

---

## Bước 4: Thiết Lập Môi Trường Ảo

1. **Tạo môi trường ảo:**
   Bên trong thư mục `e-commerce website`, tạo môi trường ảo:

   ```bash
   virtualenv venv
   ```

2. **Kích hoạt môi trường ảo:**
   - Trên **Windows**:

     ```bash
     venv\Scripts\activate
     ```

   - Trên **macOS/Linux**:

     ```bash
     source venv/bin/activate
     ```

   Sau khi kích hoạt, bạn sẽ thấy `(venv)` xuất hiện ở đầu dòng lệnh terminal.

---

## Bước 5: Cài Đặt Các Gói Phụ Thuộc

1. **Cài đặt từ file `requirements.txt`:**
   File `requirements.txt` nằm trong thư mục dự án, liệt kê tất cả các gói Python cần thiết để chạy dự án.

   Chạy lệnh sau để cài đặt toàn bộ:

   ```bash
   pip install -r requirements.txt
   ```

2. **Kiểm tra các gói còn thiếu** (Tùy chọn):
   Nếu không có file `requirements.txt` hoặc thiếu một số gói, bạn có thể cài thủ công từng gói. Ví dụ:

   ```bash
   pip install django
   pip install djangorestframework
   ```

---

## Bước 6: Cấu Hình Cài Đặt Dự Án

1. **Kiểm tra `settings.py`:**
   Mở file `ecom_web/settings.py` bằng trình soạn thảo và đảm bảo tất cả cấu hình đều chính xác.

2. **Cấu hình cơ sở dữ liệu:**
   Cơ sở dữ liệu mặc định của Django là SQLite, nếu dùng SQLite thì không cần cấu hình thêm. Tuy nhiên, nếu dự án dùng PostgreSQL hoặc MySQL, hãy đảm bảo cài đặt đúng trong phần `DATABASES` của `settings.py`.

   Ví dụ (cho SQLite):

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

3. **Thêm Secret Key:**
   Đảm bảo `SECRET_KEY` đã được thiết lập trong `settings.py`. Nếu chưa có, bạn có thể tạo bằng lệnh:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

   Sau đó thay thế giá trị `SECRET_KEY` trong `settings.py` bằng chuỗi vừa tạo.

4. **Bật chế độ Debug (Tùy chọn):**
   Khi phát triển cục bộ, hãy đảm bảo `DEBUG` được đặt thành `True` trong `settings.py`.

---

## Bước 7: Áp Dụng Migration

Django dùng migration để áp dụng các thay đổi schema cơ sở dữ liệu. Bạn cần chạy migration để tạo các bảng cần thiết.

1. **Chạy migration:**

   ```bash
   python manage.py migrate
   ```

Lệnh này áp dụng tất cả các migration để đảm bảo schema cơ sở dữ liệu được cập nhật.

---

## Bước 8: Tạo Tài Khoản Superuser (Tùy Chọn)

Nếu cần truy cập giao diện quản trị Django, hãy tạo tài khoản superuser bằng lệnh:

```bash
python manage.py createsuperuser
```

Bạn sẽ được yêu cầu nhập tên đăng nhập, email và mật khẩu.

---

## Bước 9: Khởi Động Server Phát Triển

1. **Chạy server Django:**
   Sau khi thiết lập xong, khởi động server phát triển Django:

   ```bash
   python manage.py runserver
   ```

2. **Truy cập trang web:**
   Mở trình duyệt và vào địa chỉ `http://127.0.0.1:8000/`. Bạn sẽ thấy dự án Django đang chạy.

---

## Bước 10: Truy Cập Giao Diện Quản Trị (Tùy Chọn)

Nếu đã tạo superuser, bạn có thể đăng nhập vào giao diện quản trị Django tại:

```
http://127.0.0.1:8000/admin/
```

Dùng thông tin đăng nhập đã tạo ở bước 8.

---

## Xử Lý Sự Cố

- **Lỗi: Thiếu module:**
  Nếu gặp lỗi về module bị thiếu, hãy cài đặt bằng pip:

  ```bash
  pip install <tên_module>
  ```

- **Lỗi cơ sở dữ liệu:**
  Nếu dùng cơ sở dữ liệu khác SQLite, hãy đảm bảo dịch vụ cơ sở dữ liệu đang chạy (PostgreSQL, MySQL,...) và thông tin kết nối trong `settings.py` là chính xác.

- **File tĩnh (Production):**
  Khi triển khai lên môi trường production, hãy thu thập các file tĩnh bằng lệnh:

  ```bash
  python manage.py collectstatic
  ```

---

Bạn đã thiết lập và chạy thành công dự án Django `e-commerce website` từ file zip!
