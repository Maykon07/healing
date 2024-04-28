from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from paciente.models import Consulta, Documento
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate

# view da pagina de cadastro
@login_required
def cadastro_medico(request):
    # verificação se o usuário já é médico
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já é médico')
        return redirect('/medicos/abrir_horario/')

    # método get
    if request.method == "GET":
        #return especialidades página
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades' : especialidades, 'is_medico':is_medico(request.user)})
    # método post
    elif request.method == "POST":
        #informações digitadas
        crm  = request.POST.get('crm')
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

        #salvando pela classe
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
            especialidade_id=especialidade,
            descricao=descricao,
            valor_consulta=valor_consulta,
            user=request.user
        )

        # salvando dados do médico
        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso!')
        return redirect('/medicos/abrir_horario/')

# abrir horários para consulta
@login_required
def abrir_horario(request):
    # só médico deve acessar essa área
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horários')
        return redirect('/usuarios/sair/')

    if request.method == "GET":
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas' : datas_abertas, 'is_medico':is_medico(request.user)})
    elif request.method == "POST":
        #recuperando data
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        #só pode abrir horários apos a data atual
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data não pode ser anterior a data atual')
            return redirect('/medicos/abrir_horario/')
        
        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
        )

        # salvando data no banco de dados
        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso')
        return redirect('/medicos/abrir_horario/')

@login_required
def consultas_medico(request):
    # só médico deve acessar essa área
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horários')
        return redirect('/usuarios/sair/')
    
    hoje = datetime.now().date()

    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)

    return render(request, 'consultas_medico.html', {'consultas_hoje':consultas_hoje, 'consultas_restantes':consultas_restantes, 'is_medico':is_medico(request.user)})

# area de consultas
@login_required
def consulta_area_medico(request, id_consulta):
    # só médico deve acessar essa área
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horários')
        return redirect('/usuarios/sair/')
    
    # recuperando consulta solicitada
    if request.method == "GET":
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta_area_medico.html', {'consulta':consulta, 'documentos':documentos})
    elif request.method == "POST":
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')

        # status da consulta
        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta foi cancelada.')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif consulta.status == 'F':
            messages.add_message(request, constants.WARNING, 'Essa consulta foi finalizada.')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        consulta.link = link
        consulta.status = 'I'
        consulta.save()

        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
# finalizando consulta
@login_required
def finalizar_consulta(request, id_consulta):
    # só médico deve acessar essa área
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horários')
        return redirect('/usuarios/sair/')
    
    consulta = Consulta.objects.get(id=id_consulta)

    # verificação se a solicitação é do usuário logado
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua')
        return redirect(f'/medicos/abrir_horario/')

    consulta.status = 'F'
    consulta.save()

    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

# adicionando documentos
@login_required
def add_documento(request, id_consulta):
    # só médico deve acessar essa área
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horários')
        return redirect('/usuarios/sair/')
    
    consulta = Consulta.objects.get(id=id_consulta)

    # verificando se é o usuário logado
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua')
        return redirect(f'/medicos/abrir_horario/')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    # documento é obrigatório
    if not documento:
        messages.add_message(request, constants.ERROR, 'Preencha o campo documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento
    )

    documento.save()

    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

@login_required
def dashboard(request):
    # só médico deve acessar essa área
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horários')
        return redirect('/usuarios/sair/')

    consultas = Consulta.objects.filter(data_aberta__user=request.user)\
    .filter(data_aberta__data__range=[datetime.now().date() - timedelta(days=7), datetime.now().date() + timedelta(days=1)])\
    .annotate(data_truncada=TruncDate('data_aberta__data'))\
    .values('data_truncada').annotate(quantidade=Count('id'))

    datas = [i['data_aberta__data'].strftime("%d-%m-%Y") for i in consultas]
    print(datas)
    quantidade = [i['quantidade'] for i in consultas]
    print(quantidade)

    return render(request, 'dashboard.html', {'datas':datas, 'quantidade':quantidade})