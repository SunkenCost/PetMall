from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tq%piy+c3pntex*%)7m&1xoo1&1hb6cp2v42eyqaj)%f%jxc&5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*', '114.215.167.184', 'localhost', '127.0.0.1']

# 环境变量：在 Docker 中会自动使用 'db'，本地开发时使用 '127.0.0.1'
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



# 根据数据库地址自动选择端口：本地开发用 3307，Docker 内部用 3306
DB_PORT = '3307' if DB_HOST == '127.0.0.1' else '3306'

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
