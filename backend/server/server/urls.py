from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/commodity/', include('commodity.urls')),
    path('api/shopper/', include('shopper.urls')),
    path('api/agent/', include('agent.urls')),
    path('api/merchant/', include('merchant.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

