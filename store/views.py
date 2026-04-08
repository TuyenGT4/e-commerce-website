from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail

from decimal import Decimal
import hashlib
import hmac
import urllib.parse
from datetime import datetime

import requests

from plugin.service_fee import calculate_service_fee
from plugin.paginate_queryset import paginate_queryset
from plugin.tax_calculation import tax_calculation

from store import models as store_models
from customer import models as customer_models
from vendor import models as vendor_models
from userauths import models as userauths_models

def clear_cart_items(request):
    try:
        cart_id = request.session['cart_id']
        store_models.Cart.objects.filter(cart_id=cart_id).delete()
    except:
        pass
    return

def send_order_email(order):
    """Gửi email xác nhận đơn hàng cho khách hàng và nhà bán hàng"""
    # Email cho khách hàng
    customer_merge_data = {
        'order': order,
        'order_items': order.order_items(),
    }
    subject = "Đơn hàng mới!"
    text_body = render_to_string("email/order/customer/customer_new_order.txt", customer_merge_data)
    html_body = render_to_string("email/order/customer/customer_new_order.html", customer_merge_data)

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=settings.FROM_EMAIL,
        to=[order.address.email],
        body=text_body
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()

    # Email cho từng nhà bán hàng
    for item in order.order_items():
        vendor_merge_data = {'item': item}
        subject = "Đơn hàng mới!"
        text_body = render_to_string("email/order/vendor/vendor_new_order.txt", vendor_merge_data)
        html_body = render_to_string("email/order/vendor/vendor_new_order.html", vendor_merge_data)

        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.FROM_EMAIL,
            to=[item.vendor.email],
            body=text_body
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

def index(request):
    products = store_models.Product.objects.filter(status="Published")
    categories = store_models.Category.objects.all()
    
    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "store/index.html", context)

def shop(request):
    products_list = store_models.Product.objects.filter(status="Published")
    categories = store_models.Category.objects.all()
    colors = store_models.VariantItem.objects.filter(variant__name='Color').values('title', 'content').distinct()
    sizes = store_models.VariantItem.objects.filter(variant__name='Size').values('title', 'content').distinct()
    item_display = [
        {"id": "1", "value": 1},
        {"id": "2", "value": 2},
        {"id": "3", "value": 3},
        {"id": "40", "value": 40},
        {"id": "50", "value": 50},
        {"id": "100", "value": 100},
    ]

    ratings = [
        {"id": "1", "value": "★☆☆☆☆"},
        {"id": "2", "value": "★★☆☆☆"},
        {"id": "3", "value": "★★★☆☆"},
        {"id": "4", "value": "★★★★☆"},
        {"id": "5", "value": "★★★★★"},
    ]

    prices = [
        {"id": "lowest", "value": "Giá cao đến thấp"},
        {"id": "highest", "value": "Giá thấp đến cao"},
    ]


    print(sizes)

    products = paginate_queryset(request, products_list, 10)

    context = {
        "products": products,
        "products_list": products_list,
        "categories": categories,
         'colors': colors,
        'sizes': sizes,
        'item_display': item_display,
        'ratings': ratings,
        'prices': prices,
    }
    return render(request, "store/shop.html", context)

def category(request, id):
    category = store_models.Category.objects.get(id=id)
    products_list = store_models.Product.objects.filter(status="Published", category=category)

    query = request.GET.get("q")
    if query:
        products_list = products_list.filter(name__icontains=query)

    products = paginate_queryset(request, products_list, 10)

    context = {
        "products": products,
        "products_list": products_list,
        "category": category,
    }
    return render(request, "store/category.html", context)

def vendors(request):
    vendors = userauths_models.Profile.objects.filter(user_type="Vendor")
    
    context = {
        "vendors": vendors
    }
    return render(request, "store/vendors.html", context)

def product_detail(request, slug):
    product = store_models.Product.objects.get(status="Published", slug=slug)
    product_stock_range = range(1, product.stock + 1)

    related_products = store_models.Product.objects.filter(category=product.category).exclude(id=product.id)

    context = {
        "product": product,
        "product_stock_range": product_stock_range,
        "related_products": related_products,
    }
    return render(request, "store/product_detail.html", context)

def add_to_cart(request):
    # Get parameters from the request (ID, color, size, quantity, cart_id)
    id = request.GET.get("id")
    qty = request.GET.get("qty")
    color = request.GET.get("color")
    size = request.GET.get("size")
    cart_id = request.GET.get("cart_id")
    
    request.session['cart_id'] = cart_id

    # Validate required fields
    if not id or not qty or not cart_id:
        return JsonResponse({"error": "Vui lòng chọn màu sắc hoặc kích cỡ"}, status=400)

    # Try to fetch the product, return an error if it doesn't exist
    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Không tìm thấy sản phẩm"}, status=404)

    # Check if the item is already in the cart
    existing_cart_item = store_models.Cart.objects.filter(cart_id=cart_id, product=product).first()

    # Check if quantity that user is adding exceed item stock qty
    if int(qty) > product.stock:
        return JsonResponse({"error": "Số lượng vượt quá tồn kho hiện tại"}, status=404)

    # If the item is not in the cart, create a new cart entry
    if not existing_cart_item:
        cart = store_models.Cart()
        cart.product = product
        cart.qty = qty
        cart.price = product.price
        cart.color = color
        cart.size = size
        cart.sub_total = Decimal(product.price) * Decimal(qty)
        cart.shipping = Decimal(product.shipping) * Decimal(qty)
        cart.total = cart.sub_total + cart.shipping
        cart.user = request.user if request.user.is_authenticated else None
        cart.cart_id = cart_id
        cart.save()

        message = "Item added to cart"
    else:
        # If the item exists in the cart, update the existing entry
        existing_cart_item.color = color
        existing_cart_item.size = size
        existing_cart_item.qty = qty
        existing_cart_item.price = product.price
        existing_cart_item.sub_total = Decimal(product.price) * Decimal(qty)
        existing_cart_item.shipping = Decimal(product.shipping) * Decimal(qty)
        existing_cart_item.total = existing_cart_item.sub_total +  existing_cart_item.shipping
        existing_cart_item.user = request.user if request.user.is_authenticated else None
        existing_cart_item.cart_id = cart_id
        existing_cart_item.save()

        message = "Cart updated"

    # Count the total number of items in the cart
    total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id)
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']

    # Return the response with the cart update message and total cart items
    return JsonResponse({
        "message": message ,
        "total_cart_items": total_cart_items.count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total),
        "item_sub_total": "{:,.2f}".format(existing_cart_item.sub_total) if existing_cart_item else "{:,.2f}".format(cart.sub_total) 
    })

def cart(request):
    if "cart_id" in request.session:
        cart_id = request.session['cart_id']
    else:
        cart_id = None

    items = store_models.Cart.objects.filter(cart_id=cart_id)
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']
    
    try:
        addresses = customer_models.Address.objects.filter(user=request.user)
    except:
        addresses = None

    if not items:
        messages.warning(request, "Giỏ hàng của bạn đang trống")
        return redirect("store:index")

    context = {
        "items": items,
        "cart_sub_total": cart_sub_total,
        "addresses": addresses,
    }
    return render(request, "store/cart.html", context)

def delete_cart_item(request):
    id = request.GET.get("id")
    item_id = request.GET.get("item_id")
    cart_id = request.GET.get("cart_id")
    
    # Validate required fields
    if not id and not item_id and not cart_id:
        return JsonResponse({"error": "Không tìm thấy sản phẩm"}, status=400)

    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Không tìm thấy sản phẩm"}, status=404)

    # Check if the item is already in the cart
    item = store_models.Cart.objects.get(product=product, id=item_id)
    item.delete()

    # Count the total number of items in the cart
    total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id)
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']

    return JsonResponse({
        "message": "Đã xóa sản phẩm khỏi giỏ hàng",
        "total_cart_items": total_cart_items.count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total) if cart_sub_total else 0.00
    })

def create_order(request):
    if request.method == "POST":
        address_id = request.POST.get("address")
        if not address_id:
            messages.warning(request, "Vui lòng chọn địa chỉ giao hàng để tiếp tục")
            return redirect("store:cart")
        
        address = customer_models.Address.objects.filter(user=request.user, id=address_id).first()

        if "cart_id" in request.session:
            cart_id = request.session['cart_id']
        else:
            cart_id = None

        items = store_models.Cart.objects.filter(cart_id=cart_id)
        cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']
        cart_shipping_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(shipping = models.Sum("shipping"))['shipping']
        
        order = store_models.Order()
        order.sub_total = cart_sub_total
        order.customer = request.user
        order.address = address
        order.shipping = cart_shipping_total
        order.tax = tax_calculation(cart_sub_total)
        order.total = order.sub_total + order.shipping + Decimal(order.tax)
        order.service_fee = calculate_service_fee(order.total)
        order.total += order.service_fee
        order.initial_total = order.total
        order.save()

        for i in items:
            store_models.OrderItem.objects.create(
                order=order,
                product=i.product,
                qty=i.qty,
                color=i.color,
                size=i.size,
                price=i.price,
                sub_total=i.sub_total,
                shipping=i.shipping,
                tax=tax_calculation(i.sub_total),
                total=i.total,
                initial_total=i.total,
                vendor=i.product.vendor
            )

            order.vendors.add(i.product.vendor)
        
    
    return redirect("store:checkout", order.order_id)

def coupon_apply(request, order_id):
    print("Order Id ========", order_id)
    
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        order_items = store_models.OrderItem.objects.filter(order=order)
    except store_models.Order.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn hàng")
        return redirect("store:cart")

    if request.method == 'POST':
        coupon_code = request.POST.get("coupon_code")
        
        if not coupon_code:
            messages.error(request, "Vui lòng nhập mã giảm giá")
            return redirect("store:checkout", order.order_id)
            
        try:
            coupon = store_models.Coupon.objects.get(code=coupon_code)
        except store_models.Coupon.DoesNotExist:
            messages.error(request, "Mã giảm giá không tồn tại")
            return redirect("store:checkout", order.order_id)
        
        if coupon in order.coupons.all():
            messages.warning(request, "Mã giảm giá này đã được áp dụng")
            return redirect("store:checkout", order.order_id)
        else:
            # Assuming coupon applies to specific vendor items, not globally
            total_discount = 0
            for item in order_items:
                if coupon.vendor == item.product.vendor and coupon not in item.coupon.all():
                    item_discount = item.total * coupon.discount / 100  # Discount for this item
                    total_discount += item_discount

                    item.coupon.add(coupon) 
                    item.total -= item_discount
                    item.saved += item_discount
                    item.applied_coupon = True
                    item.save()

            # Apply total discount to the order after processing all items
            if total_discount > 0:
                order.coupons.add(coupon)
                order.total -= total_discount
                order.sub_total -= total_discount
                order.saved += total_discount
                order.save()
        
        messages.success(request, "Áp dụng mã giảm giá thành công")
        return redirect("store:checkout", order.order_id)

def checkout(request, order_id):
    """Trang thanh toán — hiển thị thông tin đơn hàng và các phương thức thanh toán"""
    order = store_models.Order.objects.get(order_id=order_id)

    # Tạo URL QR Code VietQR
    vietqr_url = (
        f"https://img.vietqr.io/image/{settings.VIETQR_BANK_ID}"
        f"-{settings.VIETQR_ACCOUNT_NO}-compact2.png"
        f"?amount={int(order.total)}"
        f"&addInfo=DH{order.order_id}"
        f"&accountName={settings.VIETQR_ACCOUNT_NAME}"
    )

    context = {
        "order": order,
        "vietqr_url": vietqr_url,
        "vnpay_tmn_code": settings.VNPAY_TMN_CODE,
        "vietqr_bank_id": settings.VIETQR_BANK_ID,
        "vietqr_account_no": settings.VIETQR_ACCOUNT_NO,
        "vietqr_account_name": settings.VIETQR_ACCOUNT_NAME,
    }
    return render(request, "store/checkout.html", context)

def cod_payment(request, order_id):
    """Thanh toán khi nhận hàng (COD)"""
    order = store_models.Order.objects.get(order_id=order_id)

    if order.payment_status == "Processing":
        # COD: vẫn giữ trạng thái Processing vì chưa nhận được tiền mặt
        order.payment_method = "COD"
        order.save()

        clear_cart_items(request)

        # Tạo thông báo cho khách hàng
        customer_models.Notifications.objects.create(
            type="New Order",
            user=request.user
        )

        # Tạo thông báo cho nhà bán hàng
        for item in order.order_items():
            vendor_models.Notifications.objects.create(
                type="New Order",
                user=item.vendor
            )

        # Gửi email xác nhận
        try:
            send_order_email(order)
        except Exception as e:
            print(f"Lỗi gửi email: {e}")

        return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")

    return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")


def vnpay_payment(request, order_id):
    """Tạo URL thanh toán VNPay và redirect"""
    order = store_models.Order.objects.get(order_id=order_id)

    # Tạo các tham số VNPay theo tài liệu API
    vnp_params = {
        'vnp_Version': '2.1.0',
        'vnp_Command': 'pay',
        'vnp_TmnCode': settings.VNPAY_TMN_CODE,
        'vnp_Amount': int(order.total) * 100,  # VNPay tính theo đơn vị nhỏ nhất (x100)
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': str(order.order_id),
        'vnp_OrderInfo': f'Thanh toan don hang {order.order_id}',
        'vnp_OrderType': 'other',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': settings.VNPAY_RETURN_URL,
        'vnp_IpAddr': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
    }

    # Sắp xếp tham số theo thứ tự alphabet
    sorted_params = sorted(vnp_params.items())
    query_string = urllib.parse.urlencode(sorted_params)

    # Tạo chữ ký HMAC-SHA512
    hmac_hash = hmac.new(
        settings.VNPAY_HASH_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha512
    )
    vnp_secure_hash = hmac_hash.hexdigest()

    # Tạo URL thanh toán
    payment_url = (
        f"{settings.VNPAY_PAYMENT_URL}"
        f"?{query_string}"
        f"&vnp_SecureHash={vnp_secure_hash}"
    )

    return redirect(payment_url)


def vnpay_return(request):
    """Xử lý callback từ VNPay sau khi thanh toán"""
    vnp_params = request.GET.dict()
    vnp_secure_hash = vnp_params.pop('vnp_SecureHash', '')
    vnp_params.pop('vnp_SecureHashType', '')

    # Sắp xếp và tạo lại chữ ký để xác thực
    sorted_params = sorted(vnp_params.items())
    query_string = urllib.parse.urlencode(sorted_params)

    hmac_hash = hmac.new(
        settings.VNPAY_HASH_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha512
    )
    expected_hash = hmac_hash.hexdigest()

    # Xác thực chữ ký
    if expected_hash != vnp_secure_hash:
        messages.error(request, "Xác thực thanh toán thất bại")
        return redirect("store:index")

    # Lấy thông tin đơn hàng
    order_id = vnp_params.get('vnp_TxnRef')
    vnp_response_code = vnp_params.get('vnp_ResponseCode')

    try:
        order = store_models.Order.objects.get(order_id=order_id)
    except store_models.Order.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn hàng")
        return redirect("store:index")

    # Kiểm tra kết quả thanh toán
    if vnp_response_code == '00':
        if order.payment_status == "Processing":
            order.payment_status = "Paid"
            order.payment_method = "VNPay"
            order.payment_id = vnp_params.get('vnp_TransactionNo', '')
            order.save()

            clear_cart_items(request)

            # Tạo thông báo
            customer_models.Notifications.objects.create(
                type="New Order",
                user=request.user
            )
            for item in order.order_items():
                vendor_models.Notifications.objects.create(
                    type="New Order",
                    user=item.vendor
                )

            # Gửi email xác nhận
            try:
                send_order_email(order)
            except Exception as e:
                print(f"Lỗi gửi email: {e}")

            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")

    return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")


def vietqr_confirm(request, order_id):
    """Trang xác nhận thanh toán VietQR — hiển thị QR và chờ admin xác nhận"""
    order = store_models.Order.objects.get(order_id=order_id)

    vietqr_url = (
        f"https://img.vietqr.io/image/{settings.VIETQR_BANK_ID}"
        f"-{settings.VIETQR_ACCOUNT_NO}-compact2.png"
        f"?amount={int(order.total)}"
        f"&addInfo=DH{order.order_id}"
        f"&accountName={settings.VIETQR_ACCOUNT_NAME}"
    )

    context = {
        "order": order,
        "vietqr_url": vietqr_url,
        "bank_id": settings.VIETQR_BANK_ID,
        "account_no": settings.VIETQR_ACCOUNT_NO,
        "account_name": settings.VIETQR_ACCOUNT_NAME,
    }
    return render(request, "store/vietqr_confirm.html", context)


def payment_status(request, order_id):
    """Trang hiển thị trạng thái thanh toán"""
    order = store_models.Order.objects.get(order_id=order_id)
    payment_status = request.GET.get("payment_status")

    context = {
        "order": order,
        "payment_status": payment_status,
    }
    return render(request, "store/payment_status.html", context)

def payment_status(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    payment_status = request.GET.get("payment_status")

    context = {
        "order": order,
        "payment_status": payment_status
    }
    return render(request, "store/payment_status.html", context)

def filter_products(request):
    products = store_models.Product.objects.all()

    # Get filters from the AJAX request
    categories = request.GET.getlist('categories[]')
    rating = request.GET.getlist('rating[]')
    sizes = request.GET.getlist('sizes[]')
    colors = request.GET.getlist('colors[]')
    price_order = request.GET.get('prices')
    search_filter = request.GET.get('searchFilter')
    display = request.GET.get('display')

    print("categories =======", categories)
    print("rating =======", rating)
    print("sizes =======", sizes)
    print("colors =======", colors)
    print("price_order =======", price_order)
    print("search_filter =======", search_filter)
    print("display =======", display)

   
    # Apply category filtering
    if categories:
        products = products.filter(category__id__in=categories)

    # Apply rating filtering
    if rating:
        products = products.filter(reviews__rating__in=rating).distinct()

    

    # Apply size filtering
    if sizes:
        products = products.filter(variant__variant_items__content__in=sizes).distinct()

    # Apply color filtering
    if colors:
        products = products.filter(variant__variant_items__content__in=colors).distinct()

    # Apply price ordering
    if price_order == 'lowest':
        products = products.order_by('-price')
    elif price_order == 'highest':
        products = products.order_by('price')

    # Apply search filter
    if search_filter:
        products = products.filter(name__icontains=search_filter)

    if display:
        products = products.filter()[:int(display)]


    # Render the filtered products as HTML using render_to_string
    html = render_to_string('partials/_store.html', {'products': products})

    return JsonResponse({'html': html, 'product_count': products.count()})

def order_tracker_page(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        return redirect("store:order_tracker_detail", item_id)
    
    return render(request, "store/order_tracker_page.html")

def order_tracker_detail(request, item_id):
    try:
        item = store_models.OrderItem.objects.filter(models.Q(item_id=item_id) | models.Q(tracking_id=item_id)).first()
    except:
        item = None
        messages.error(request, "Order not found!")
        return redirect("store:order_tracker_page")
    
    context = {
        "item": item,
    }
    return render(request, "store/order_tracker.html", context)

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        userauths_models.ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message,
        )
        messages.success(request, "Message sent successfully")
        return redirect("store:contact")
    return render(request, "pages/contact.html")

def faqs(request):
    return render(request, "pages/faqs.html")

def privacy_policy(request):
    return render(request, "pages/privacy_policy.html")

def terms_conditions(request):
    return render(request, "pages/terms_conditions.html")