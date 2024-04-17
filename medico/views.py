from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
#from django.contrib.auth.decorators import login_required


def cadastro_medico(request):
    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html',{'especialidades': especialidades})
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

       # Validar todos os campos

        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta,
            user=request.user
        )

        dados_medico.save()
        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso')
        return redirect('/medicos/abrir_horario') #vai dar erro, implementar 'abrir_horario' amanha
