# pip install pycryptodome
# pip install python-alipay-sdk

from alipay import AliPay
import time
alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnyo8bCCQR7K980byTqj6sm7SrAEBj15820lk4mpw8AUBVVfsoqqdP89zDQFoSaQxaCh4ZUiibfnHTKP7Kbcj3GLkSrY+IU/AqRohoq5tjcl5zKnjtHjaE/lvKqkf8LeJol/KgjU/FxOeajOGAjnYSITm5MyQwqa8bIqiA0SUkB6QFC/6N7KedHfo2+r4k5AscyDdkfHUv3aCha7FfGy5udI0Zx39v+HOlKAF9aWbhzu8LpqJZdGI4qC2M87firT8I3FmxUbr2LOQldLOMyb6ZIQewyMzzA6HZDacbson/4mGhPqft32mjp0HVgJq4MAUKEVIcEKoy8gDJC8iSjx8FwIDAQAB
-----END PUBLIC KEY-----"""
app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAnyo8bCCQR7K980byTqj6sm7SrAEBj15820lk4mpw8AUBVVfsoqqdP89zDQFoSaQxaCh4ZUiibfnHTKP7Kbcj3GLkSrY+IU/AqRohoq5tjcl5zKnjtHjaE/lvKqkf8LeJol/KgjU/FxOeajOGAjnYSITm5MyQwqa8bIqiA0SUkB6QFC/6N7KedHfo2+r4k5AscyDdkfHUv3aCha7FfGy5udI0Zx39v+HOlKAF9aWbhzu8LpqJZdGI4qC2M87firT8I3FmxUbr2LOQldLOMyb6ZIQewyMzzA6HZDacbson/4mGhPqft32mjp0HVgJq4MAUKEVIcEKoy8gDJC8iSjx8FwIDAQABAoIBAHQ8jxXUDioeUfQ5armhVDw9DOOKdI40TfCDQAbN/x56OUgPRwRgnyg7ouTrkzK8k0xiydIF4oF4OWEyHDmRwsGvAtPBFcyUBro4GDpLMjyq16VsqJti6rhNoC7Chk3wa7ZGSIkgw6thq34ZlJNJlTcYv9p1vn448EBAWiMS0YARepRoWYcCHeJzWUCGIICph22tdCWS7d3MUYPD+VN2UbdVKXx1zlVyCQ2kuJraH+NU3awZnluUuHpaJ5DP8le1GwRaOjyzC+h7V49SAW96ZXjaspew4hB0uUNtZ5mZ1+7W5qTjK6R0/A30CTo/qGbAUS+EQJtTjcfnd1IIQ8NrMBkCgYEA1VZ3lHoxRJhaFRV7hTIW14gUwJFJfHElXL0KZxgVHBZGQ8VmZPdOE2a+VeHM7MR7qG+RiubnGfVSaXLoYDJi8Ar9X4Bkki60lKvPR4Bm4SB98y2UAL0oEbPFAJL3ivwevcIuWqQE2eUvxcWV9YCRV8IvPTcBkG5qOvSLZXMX+l0CgYEAvv532oDNqyitpeIHJKcOfmyFhDaa/JB7Hj3Q7IYd2lbS40GeYNKhgc85hP1chZaicHUiXdJINsIzoCyG0n0r5qKgyMCfUMg8p96v8l9wIlHnRIjOI+4PQbbDNHikeLZr9VgxCJEbZUT4VdGRTZVpAv5RDSgl27/Y+DHIBnEf8QMCgYABV1XRHSOKJtsKHuRz5ei22ignPcKUgbGWb6nNFB2t24X9jxQhtlxLSu4PZCgBpQqR+IGVufXh9+TYvNwxHp/4mlkVbJ01Pg3skVfwPyJmb+nayYKQrp+93L90TXg463TWBI5+C2HsbMBsId3beT9wqcvaOqpL2iXY0Qi/ToXsEQKBgBSFv1cpM/BKRK5oZSAZG0OWYZpdS7YLyE7tkX94wchuP+bPbDc3KseJ/sI9fy2TjAzNaU3vhHbt0yJI5ovDi24S13f6yqOhgHMBSKKggqoNZu5ETPIraFRFUSBYPkQCRgNs4IftH6Z4DL8b76MIhOofbZIeWEMOkD/LCZU3npkFAoGBAL+hHQsD4qTbQd6uIycXZWiIaesMmRpd5sNkR12euR61TQc1sgevzn0DlcoPB+CbzP+wDph6+oKIRwCOq/YEzAEx19yPvVUj40MldaOAZke/icB3gAQQ0k/5gx6m9TeTxkLGiYDgPiTEjwgLrSZmxSknqOVgfH54kA+MGA+ZYPdf
-----END RSA PRIVATE KEY-----"""

def get_pay(out_trade_no, total_amount, return_url):
    # 实例化支付应用
    alipay = AliPay(
        appid="9021000138622595",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )
    # 发起支付请求
    order_string = alipay.api_alipay_trade_page_pay(
        # 订单号，每次发送请求都不能一样
        out_trade_no=out_trade_no,
        # 支付金额
        total_amount=str(total_amount),
        # 交易信息
        subject="测试",
        return_url=return_url + '?t=' + out_trade_no,
        notify_url=return_url + '?t=' + out_trade_no
    )
    print('https://openapi-sandbox.dl.alipaydev.com/gateway.do?'+ order_string)
    return 'https://openapi-sandbox.dl.alipaydev.com/gateway.do?'+ order_string
