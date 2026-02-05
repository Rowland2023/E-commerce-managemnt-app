"""
URL configuration for ecommerceapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from store.admin import mysite
def home(request):
    return HttpResponse("Welcome to the Ecommerce Home Page!")
urlpatterns = [
    # Django admin
    path("", home),
    path('admin/', mysite.urls),
    # API routes from your store app
    path('', include('store.urls')),

    # DRF login/logout views for the browsable API

]

