
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
]

handler404 = 'website.views.error_404'
handler500 = 'website.views.error_500'