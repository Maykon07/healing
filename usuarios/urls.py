from django.urls import path
from . import views  #import views

#url pagina de cadastro
urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"),
    path('login/', views.login_view, name="login"),
    path('sair/', views.sair, name="sair")
]