from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth

# cadastro de usuário
def cadastro(request):
    if request.method == "GET":
        #cadastro.html
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        #submit
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # senhas precisam ser iguais
        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, "A senha e o confirmar senha devem ser iguais")
            return redirect('/usuarios/cadastro/')
        
        # tamanho da senha precia ser 6
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, "A senha deve ter mais de 6 dígitos")
            return redirect('/usuarios/cadastro/')
        
        #verificação de repetidos
        users = User.objects.filter(username=username)
        
        if users.exists():
            messages.add_message(request, constants.ERROR, "Já existe um usuário com esse nome")
            return redirect('/usuarios/cadastro/')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )

        return redirect('/usuarios/login/')
    
def login_view(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        # verificar se existe o user no banco de dados
        user = auth.authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user) #login
            return redirect('/pacientes/home/')
        
        messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos')
        return redirect('/usuarios/login/')
    
def sair(request):
    auth.logout(request) #logout
    return redirect('/usuarios/login/')