from alipay import AliPay
from django.conf import settings


def get_alipay_instance():
    """获取支付宝 SDK 实例"""
    return AliPay(
        appid=settings.ALIPAY_APP_ID,
        app_notify_url=settings.ALIPAY_APP_NOTIFY_URL,
        app_private_key_string=settings.ALIPAY_APP_PRIVATE_KEY,
        alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY,
        sign_type="RSA2",
        debug=settings.DEBUG,  # 跟随 Django DEBUG 设置，生产自动切换为正式环境
    )


def get_pay_url(out_trade_no, total_amount, subject, return_url):
    """生成支付宝PC网站支付链接
    
    Args:
        out_trade_no: 商户订单号
        total_amount: 订单总金额（元）
        subject: 订单标题
        return_url: 支付完成后同步跳转地址
        
    Returns:
        str: 完整的支付宝支付页面URL
    """
    alipay = get_alipay_instance()
    
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=out_trade_no,
        total_amount=str(total_amount),
        subject=subject,
        return_url=return_url,
        notify_url=settings.ALIPAY_APP_NOTIFY_URL,
    )
    
    return f"{settings.ALIPAY_GATEWAY}?{order_string}"


def verify_alipay_callback(data):
    """验证支付宝异步回调签名
    
    Args:
        data: 支付宝回调的参数字典
        
    Returns:
        bool: 签名验证是否通过
    """
    alipay = get_alipay_instance()
    
    # 【修复】必须用 pop 把 sign 和 sign_type 剔除出字典，否则参与签名生成会导致验证永远失败
    data_copy = data.copy()
    signature = data_copy.pop("sign", "")
    data_copy.pop("sign_type", None)
    
    success = alipay.verify(data_copy, signature)
    return success
