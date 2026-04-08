from decimal import Decimal

# Thuế GTGT (VAT) Việt Nam: 10% (Nghị định 15/2022/NĐ-CP)
VAT_RATE = Decimal('0.10')

def tax_calculation(order_total):
    """
    Tính thuế VAT 10% theo quy định Việt Nam.
    Tham số:
        order_total: Tổng giá trị đơn hàng (số hoặc Decimal)
    Trả về:
        Số tiền thuế VAT (Decimal)
    """
    return Decimal(str(order_total)) * VAT_RATE