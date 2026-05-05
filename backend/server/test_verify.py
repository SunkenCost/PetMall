from alipay import AliPay

ALIPAY_APP_ID = "9021000163622422"

ALIPAY_APP_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAmnmUnaLMdoOxjP06i9aGSko/SY1sNrZzzUjLJVNgpzDD/ZLzmqTEM3VoP0eThWEWrEGceZk6QdsjAZWnQVaXUaTZQTxoGr3ewRoNfccZxq15ktokxvT/8rxAaEKIIEQ1M/uUxr1KCqhrapF4tfNWEuCipvndKRYaQeBe8qOR7O7FAGVpYR7Tds3MS7JgCe/Rgxdczzwm/WRqX6PjhdBa9Tqt5zwOJLcYXVCmCZ9b+XvRhQhxusGv1WNFdu8EDHWo0svQVDCgPKi4WQBrV+QU+nv74loRUu9Sb4A1ouhdfcwxkKX/bCpBd8iaR+53ptHzpsOXZzfbGTlvIIkS7hDjOQIDAQABAoIBAC/39zVoO3PF+1mbvRV1fWgOXE670tG+oIErzKF/nbDtTL8uZeUsqxyLpd6YnG+7sW22Rh/gfB29LcatMS3x9LVOqoQ+fNlpAoYWUAAx1ohCkFEQ2oDJzb0TxjBaEKlsZNUKl62LVDWxDQIfwEtID/92sCuHxayfh3HTeciBEKxxD7REckcjllspjhmaEeknilYA2mG5JJTWKKWLRKThioceq6IHyPSHwYfoPj+Ps6K5enOqL34O8XIdKTWq3YvNfBitW68QVoEMCp4tGNVg0Kjo+4BT7BQySmfD3izLy/7eFGvURyQnun77pk1/mEaTpyFY3+NXCkMcfIfOl25K6gECgYEA6Xy753sjg3UalOIP8MH9j+TnVB4RQllLYrNLUxzyJkEJhLQlWicfJUMF+3vTX+u7Jcy+FhZ5I561hq1fBHkIiqOHEshlkpqSquPZIvm7sYs5akvM0jypRsB39Ph7oWbbv1Y2Ml6bKhwOLCzKifnxhryTaBUoMUYJNyYgg2IXb/kCgYEAqV6NL0h9ymsXCr3mkeiqX1X3xleIrhkDL7Q/LUVUTqJKDvAZWEvtlploXSTMb1mA2qa1kZ28mO4zvDX08arcaFzDC0FZV6g3y1ajyrU14q1RYcIIZ5P8X8M7JiC1J++D1V3JxJ6S8eNuYpGpxjmDbkxrXf/YHlT4ssxRDBHwXUECgYEAzPi4iI0cbyIVlNAkCEp0y6a6wainpCR5vosBvFPz7Es6DOqMw+kGOZLuJIje1h0+rP9hfEh8Th3c4/89I9MRAYxvXrjYGmxiB22AyGiOMl2zqLIkfAfO3xLF/CNLfTSsAvuvFmbhNoVsl7E2mQv30T2o9j1kjGUcX/KzpkMtqhkCgYEAjEe09mm7TlF+hzYcZ9NmcYoZq9zKZzBuVC+deBiJKIwAfPjedSSGR4sORr941+0w7WjQ0CfuklgQ351tIFDdN09FeOgKYLECbVd4WCfY1sOouShln6yRhpuEPSMwCEC4V5vTxxd0LAasYdW14Wm3cz62WufSD+VfC3Bw3GdrR0ECgYB8OgnjyXYJfsq52IJ1Av5ElBTY5/pF+4TZR+NzNfLM0wJsCpcOEN26evZqee8j/u0xr/gw+cp784lfVYTJIc2FTodpbuQzVIlyxbZFPCStP/AcVYq7ZqGIJt7cBQqpz9OECs+9lBF9oFUy8mxSoG7lA1QqtU2c8LafchQrisNhvg==
-----END RSA PRIVATE KEY-----"""

ALIPAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnddw1NJqCghhA5mtvQAZE4f9teGD4bJeDSm3viz4LMPa31w9d9ST1huWUWJhdVkjJrRAWAf27XTqR/Yasq2VcSquaqWw5oOQGnSsrMjDnDtqTn4xh3mbBtz3TbOnMmtxazeK9N0sq9C2BvtgUdc79uWu5InIR0RF+uScJX1PYwzkq8E7mh4v1yV4mfR1AGJ060l/5hMgLI3HqGZDKPZws7tIl6a5frB03HPPwc9KLfqztJQRYeExJk5H4N4KhbjOo85VfA06VHKF6mHuVITAMu8NfAkMT+8Hbazh6rPQvqHnCyxtqpDOhT/qyJRIXiLzWagMszIu/5h3PhboUr1dhwIDAQAB
-----END PUBLIC KEY-----"""

alipay = AliPay(
    appid=ALIPAY_APP_ID,
    app_notify_url="",
    app_private_key_string=ALIPAY_APP_PRIVATE_KEY,
    alipay_public_key_string=ALIPAY_PUBLIC_KEY,
    sign_type="RSA2",
    debug=True,
)

data = {'gmt_create': '2026-05-05 19:47:57', 'charset': 'utf-8', 'gmt_payment': '2026-05-05 19:48:05', 'notify_time': '2026-05-05 19:48:06', 'subject': '天然豆腐猫砂 6L', 'sign': 'lvMKh34mEk5H1FXkYH1lIIpX8K43pDkzCmlHFr7pukZ7tNAvKaHpdDZQfDzBMrcP9fSueJ+5glnOmuu7tEYgIXrB+BvmXn0k8PWGuiGqLJlw83tJVmBNeHwRxg44QoV2oV0B9rcfWK2Kz0bcHlRkc/NawJ3rfSdQlrTpGJLK57fjYuvDnB/DDle+GYdCiVU6dOU/8fJnJIfd/PbjoftE7cCsRi4te9vnwDXEgfjLfSDQY5SZlITGOZC0kbs486iRaCc7IXY9Ha+GdyQB0aJpKl+iTrDUxLqpjrcjfpSsWm7f15fw/NrQoSWsGCSdDYD3FmzdX5D61WKeawxBgIEN1A==', 'buyer_id': '2088722100931302', 'invoice_amount': '25.00', 'version': '1.0', 'notify_id': '2026050501222194805131300508877618', 'fund_bill_list': '[{"amount":"25.00","fundChannel":"ALIPAYACCOUNT"}]', 'notify_type': 'trade_status_sync', 'out_trade_no': 'O202605051947186122', 'total_amount': '25.00', 'trade_status': 'TRADE_SUCCESS', 'trade_no': '2026050522001431300509169740', 'auth_app_id': '9021000163622422', 'receipt_amount': '25.00', 'point_amount': '0.00', 'buyer_pay_amount': '25.00', 'app_id': '9021000163622422', 'sign_type': 'RSA2', 'seller_id': '2088721100931297'}

data1 = data.copy()
sign = data1.get("sign")
success1 = alipay.verify(data1, sign)
print("With get:", success1)

data2 = data.copy()
sign = data2.pop("sign")
success2 = alipay.verify(data2, sign)
print("With pop sign:", success2)

data3 = data.copy()
sign = data3.pop("sign")
data3.pop("sign_type")
success3 = alipay.verify(data3, sign)
print("With pop sign and sign_type:", success3)
