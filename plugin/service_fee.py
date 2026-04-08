from decimal import Decimal

# Phí dịch vụ: 5% trên tổng đơn hàng
SERVICE_FEE_RATE = Decimal('5')

def calculate_service_fee(order_total):
    """
    Tính phí dịch vụ 5% trên tổng đơn hàng.
    Tham số:
        order_total: Tổng giá trị đơn hàng (số hoặc Decimal)
    Trả về:
        Số tiền phí dịch vụ (Decimal)
    """
    return Decimal(str(order_total)) * SERVICE_FEE_RATE / Decimal('100')