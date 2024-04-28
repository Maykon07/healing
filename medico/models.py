from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# verificação se o usuário é médico 
def is_medico(user):
    return DadosMedico.objects.filter(user=user).exists()

# classe das especialidades médicas
class Especialidades(models.Model):
    especialidade = models.CharField(max_length=100) #campo de especialidade(string)

    def __str__(self):
        return self.especialidade
    
# informações dos médicos
class DadosMedico(models.Model):

    crm = models.CharField(max_length=30) #crm
    nome = models.CharField(max_length=100) #nome
    cep = models.CharField(max_length=15)   #cep
    rua = models.CharField(max_length=100)  #rua
    bairro = models.CharField(max_length=100) #bairro
    numero = models.IntegerField() #numero da casa
    rg = models.ImageField(upload_to='rgs')
    cedula_identidade_medica = models.ImageField(upload_to='cim')
    foto = models.ImageField(upload_to='fotos_perfil')
    descricao = models.TextField()
    valor_consulta = models.FloatField(default=100)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) #não faz nada se excluir o user
    especialidade = models.ForeignKey(Especialidades, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user.username
    
    @property
    def proxima_data(self):
        # primeira data disponivel após o dia de hoje
        proxima_data = DatasAbertas.objects.filter(user=self.user).filter(data__gt=datetime.now()).filter(agendado=False).order_by('data').first()
        return proxima_data

# datas disponiveis para consulta  
class DatasAbertas(models.Model):
    data = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    agendado = models.BooleanField(default=False)

    def __str__(self):
        return str(self.data)