from django.urls import path

from pages import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('rules/', views.RulesPageView.as_view(), name='rules'),
]
