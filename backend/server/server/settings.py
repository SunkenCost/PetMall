from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tq%piy+c3pntex*%)7m&1xoo1&1hb6cp2v42eyqaj)%f%jxc&5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*', '114.215.167.184', 'localhost', '127.0.0.1']

# 【数据库切换开关】
# True: 连接本地原生安装的 MySQL (默认 3306)
# False: 连接 Docker 容器映射出的 MySQL (默认 3307)
USE_LOCAL_MYSQL = True

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')


INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',
    'commodity',
    'shopper',
    'agent',
    'aftersales',
    'merchant',
    'corsheaders'
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 添加中间件LocaleMiddleware
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'



# 自动选择端口：
# 如果是本地回环地址且开启了 USE_LOCAL_MYSQL，则用 3306；否则如果是本地回环则用 3307（给 Docker 用）；
# 如果是在 Docker 容器内部（DB_HOST='db'），则直接用 3306。
if DB_HOST == '127.0.0.1':
    DB_PORT = '3306' if USE_LOCAL_MYSQL else '3307'
else:
    DB_PORT = '3306'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'e',
        'USER': 'root',
        'PASSWORD': '123456xqy',
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    # 配置分页器
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 每页的数据量
    'PAGE_SIZE': 6,
    # 用户认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# 设置跨域访问
# 指定所有域名(IP)都可以访问，默认为False
CORS_ORIGIN_ALLOW_ALL = True
# 设置允许携带Cookie
CORS_ALLOW_CREDENTIALS = True
# 设置允许访问的域名(IP)
# 如果CORS_ORIGIN_ALLOW_ALL=True则无需设置
CORS_ORIGIN_WHITELIST = []
# 允许执行的请求方式
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
# 允许执行的请求头
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

# 允许前端开发服务器通过 CSRF 校验（django_login 写入 Session 后需要此配置）
CSRF_TRUSTED_ORIGINS = [
    'http://114.215.167.184',
    'http://localhost:8010',
    'http://127.0.0.1:8000',
]

# ========== 邮件服务配置（SMTP） ==========
EMAIL_BACKEND = 'accounts.backends.Python312EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'sakuraentropia@163.com'
EMAIL_HOST_PASSWORD = 'EAkjPsuG7AqRjE2F'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 邮箱验证码有效时长（秒），默认5分钟
EMAIL_CODE_EXPIRE_SECONDS = 300

# ========== Zhipu AI Agent 配置 ==========
ZHIPU_AI_API_KEY = "807a065d7962401f8d82a8890df8321e.QjzucEerkJP4Rm5E"
ZHIPU_AI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
ZHIPU_AI_MODEL = "glm-4-flash"  # 使用免费额度模型

# ========== 支付宝沙盒支付配置 ==========
ALIPAY_APP_ID = "9021000163622422"
ALIPAY_MERCHANT_PID = "2088721100931297"  # 商户PID
ALIPAY_APP_NOTIFY_URL = "http://s34293de.natappfree.cc/api/shopper/pay/notify/"  # 异步通知URL，支付成功后支付宝调用
ALIPAY_RETURN_URL = "http://s34293de.natappfree.cc/api/shopper/pay/return/"  # 同步跳转URL
ALIPAY_GATEWAY = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"

# 应用私钥 (RSA2)
ALIPAY_APP_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAmnmUnaLMdoOxjP06i9aGSko/SY1sNrZzzUjLJVNgpzDD/ZLzmqTEM3VoP0eThWEWrEGceZk6QdsjAZWnQVaXUaTZQTxoGr3ewRoNfccZxq15ktokxvT/8rxAaEKIIEQ1M/uUxr1KCqhrapF4tfNWEuCipvndKRYaQeBe8qOR7O7FAGVpYR7Tds3MS7JgCe/Rgxdczzwm/WRqX6PjhdBa9Tqt5zwOJLcYXVCmCZ9b+XvRhQhxusGv1WNFdu8EDHWo0svQVDCgPKi4WQBrV+QU+nv74loRUu9Sb4A1ouhdfcwxkKX/bCpBd8iaR+53ptHzpsOXZzfbGTlvIIkS7hDjOQIDAQABAoIBAC/39zVoO3PF+1mbvRV1fWgOXE670tG+oIErzKF/nbDtTL8uZeUsqxyLpd6YnG+7sW22Rh/gfB29LcatMS3x9LVOqoQ+fNlpAoYWUAAx1ohCkFEQ2oDJzb0TxjBaEKlsZNUKl62LVDWxDQIfwEtID/92sCuHxayfh3HTeciBEKxxD7REckcjllspjhmaEeknilYA2mG5JJTWKKWLRKThioceq6IHyPSHwYfoPj+Ps6K5enOqL34O8XIdKTWq3YvNfBitW68QVoEMCp4tGNVg0Kjo+4BT7BQySmfD3izLy/7eFGvURyQnun77pk1/mEaTpyFY3+NXCkMcfIfOl25K6gECgYEA6Xy753sjg3UalOIP8MH9j+TnVB4RQllLYrNLUxzyJkEJhLQlWicfJUMF+3vTX+u7Jcy+FhZ5I561hq1fBHkIiqOHEshlkpqSquPZIvm7sYs5akvM0jypRsB39Ph7oWbbv1Y2Ml6bKhwOLCzKifnxhryTaBUoMUYJNyYgg2IXb/kCgYEAqV6NL0h9ymsXCr3mkeiqX1X3xleIrhkDL7Q/LUVUTqJKDvAZWEvtlploXSTMb1mA2qa1kZ28mO4zvDX08arcaFzDC0FZV6g3y1ajyrU14q1RYcIIZ5P8X8M7JiC1J++D1V3JxJ6S8eNuYpGpxjmDbkxrXf/YHlT4ssxRDBHwXUECgYEAzPi4iI0cbyIVlNAkCEp0y6a6wainpCR5vosBvFPz7Es6DOqMw+kGOZLuJIje1h0+rP9hfEh8Th3c4/89I9MRAYxvXrjYGmxiB22AyGiOMl2zqLIkfAfO3xLF/CNLfTSsAvuvFmbhNoVsl7E2mQv30T2o9j1kjGUcX/KzpkMtqhkCgYEAjEe09mm7TlF+hzYcZ9NmcYoZq9zKZzBuVC+deBiJKIwAfPjedSSGR4sORr941+0w7WjQ0CfuklgQ351tIFDdN09FeOgKYLECbVd4WCfY1sOouShln6yRhpuEPSMwCEC4V5vTxxd0LAasYdW14Wm3cz62WufSD+VfC3Bw3GdrR0ECgYB8OgnjyXYJfsq52IJ1Av5ElBTY5/pF+4TZR+NzNfLM0wJsCpcOEN26evZqee8j/u0xr/gw+cp784lfVYTJIc2FTodpbuQzVIlyxbZFPCStP/AcVYq7ZqGIJt7cBQqpz9OECs+9lBF9oFUy8mxSoG7lA1QqtU2c8LafchQrisNhvg==
-----END RSA PRIVATE KEY-----"""

# 支付宝公钥 (RSA2)
ALIPAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnddw1NJqCghhA5mtvQAZE4f9teGD4bJeDSm3viz4LMPa31w9d9ST1huWUWJhdVkjJrRAWAf27XTqR/Yasq2VcSquaqWw5oOQGnSsrMjDnDtqTn4xh3mbBtz3TbOnMmtxazeK9N0sq9C2BvtgUdc79uWu5InIR0RF+uScJX1PYwzkq8E7mh4v1yV4mfR1AGJ060l/5hMgLI3HqGZDKPZws7tIl6a5frB03HPPwc9KLfqztJQRYeExJk5H4N4KhbjOo85VfA06VHKF6mHuVITAMu8NfAkMT+8Hbazh6rPQvqHnCyxtqpDOhT/qyJRIXiLzWagMszIu/5h3PhboUr1dhwIDAQAB
-----END PUBLIC KEY-----"""
