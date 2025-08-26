from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from PIL import Image
import os


class Usuario(AbstractUser):
    """
    Modelo customizado de usuário com campos adicionais e tipos
    """
    TIPO_CHOICES = [
        ('master', 'Master'),
        ('restrito', 'Restrito'),
        ('cliente', 'Cliente'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='restrito')
    telefone = models.CharField(
        max_length=15, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Número de telefone inválido')],
        blank=True, null=True
    )
    cpf = models.CharField(
        max_length=14, 
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 'CPF deve estar no formato 000.000.000-00')],
        unique=True, blank=True, null=True
    )
    data_nascimento = models.DateField(blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfis/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Permissões granulares para usuários restritos
    pode_cadastrar_cliente = models.BooleanField(default=False)
    pode_cadastrar_funcionario = models.BooleanField(default=False)
    pode_cadastrar_cargo = models.BooleanField(default=False)
    pode_agendar = models.BooleanField(default=False)
    pode_ver_agendamentos = models.BooleanField(default=False)
    pode_ver_relatorios = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Redimensionar foto de perfil
        if self.foto_perfil:
            img = Image.open(self.foto_perfil.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.foto_perfil.path)
    
    def is_master(self):
        return self.tipo == 'master'
    
    def is_cliente(self):
        return self.tipo == 'cliente'
    
    def tem_permissao(self, permissao):
        """Verifica se o usuário tem uma permissão específica"""
        if self.is_master():
            return True
        return getattr(self, permissao, False)


class Cargo(models.Model):
    """
    Modelo para cargos/posições dos funcionários
    """
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    salario_base = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        blank=True, null=True
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def pode_excluir(self):
        """Verifica se o cargo pode ser excluído (não tem funcionários associados)"""
        return not self.funcionario_set.exists()


class Funcionario(models.Model):
    """
    Modelo para funcionários da empresa
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT)
    codigo_funcionario = models.CharField(max_length=20, unique=True)
    data_contratacao = models.DateField()
    data_demissao = models.DateField(blank=True, null=True)
    salario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['usuario__first_name', 'usuario__last_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.cargo.nome}"
    
    def save(self, *args, **kwargs):
        if not self.codigo_funcionario:
            # Gerar código único do funcionário
            ultimo_codigo = Funcionario.objects.filter(
                codigo_funcionario__startswith='FUNC'
            ).order_by('-codigo_funcionario').first()
            
            if ultimo_codigo:
                numero = int(ultimo_codigo.codigo_funcionario[4:]) + 1
            else:
                numero = 1
            
            self.codigo_funcionario = f"FUNC{numero:04d}"
        
        super().save(*args, **kwargs)
    
    def esta_ativo(self):
        """Verifica se o funcionário está ativo (não foi demitido)"""
        return self.ativo and self.data_demissao is None


class Servico(models.Model):
    """
    Modelo para serviços oferecidos pela empresa
    """
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    duracao_minutos = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)]  # Máximo 24 horas
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"
    
    def duracao_formatada(self):
        """Retorna a duração formatada em horas e minutos"""
        horas = self.duracao_minutos // 60
        minutos = self.duracao_minutos % 60
        
        if horas > 0:
            return f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"
        return f"{minutos}min"


class Agendamento(models.Model):
    """
    Modelo principal para agendamentos
    """
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
        ('em_andamento', 'Em Andamento'),
    ]
    
    cliente = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='agendamentos_cliente',
        limit_choices_to={'tipo': 'cliente'}
    )
    funcionario = models.ForeignKey(
        Funcionario, 
        on_delete=models.CASCADE,
        related_name='agendamentos_funcionario'
    )
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data_agendamento = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='agendado')
    observacoes = models.TextField(blank=True, null=True)
    valor_final = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        blank=True, null=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='agendamentos_criados'
    )
    
    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-data_agendamento']
    
    def __str__(self):
        return f"{self.cliente.get_full_name()} - {self.servico.nome} - {self.data_agendamento.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Se valor_final não foi definido, usar o preço do serviço
        if not self.valor_final:
            self.valor_final = self.servico.preco
        
        super().save(*args, **kwargs)
    
    def data_hora_fim(self):
        """Calcula a data/hora de fim baseada na duração do serviço"""
        from datetime import timedelta
        return self.data_agendamento + timedelta(minutes=self.servico.duracao_minutos)
    
    def pode_cancelar(self):
        """Verifica se o agendamento pode ser cancelado"""
        return self.status in ['agendado'] and self.data_agendamento > timezone.now()
    
    def esta_no_passado(self):
        """Verifica se o agendamento é no passado"""
        return self.data_agendamento < timezone.now()


class ConfiguracaoEmpresa(models.Model):
    """
    Modelo para configurações da empresa (Singleton)
    """
    nome_empresa = models.CharField(max_length=200, default='Minha Empresa')
    logotipo = models.ImageField(upload_to='empresa/', blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)
    whatsapp_numero = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_token = models.CharField(max_length=500, blank=True, null=True)
    whatsapp_ativo = models.BooleanField(default=False)
    mensagem_boas_vindas = models.TextField(
        default='Bem-vindo ao nosso sistema de agendamento!',
        blank=True, null=True
    )
    horario_funcionamento = models.TextField(
        default='Segunda a Sexta: 08:00 - 18:00',
        blank=True, null=True
    )
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração da Empresa'
        verbose_name_plural = 'Configurações da Empresa'
    
    def __str__(self):
        return self.nome_empresa
    
    def save(self, *args, **kwargs):
        # Garantir que só existe uma instância (Singleton)
        if not self.pk and ConfiguracaoEmpresa.objects.exists():
            raise ValueError('Só pode existir uma configuração de empresa')
        
        super().save(*args, **kwargs)
        
        # Redimensionar logotipo
        if self.logotipo:
            img = Image.open(self.logotipo.path)
            if img.height > 200 or img.width > 200:
                output_size = (200, 200)
                img.thumbnail(output_size)
                img.save(self.logotipo.path)
    
    @classmethod
    def get_instance(cls):
        """Retorna a instância única da configuração"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class LogAuditoria(models.Model):
    """
    Modelo para logs de auditoria do sistema
    """
    ACAO_CHOICES = [
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'Visualização'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=10, choices=ACAO_CHOICES)
    modelo = models.CharField(max_length=100)
    objeto_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_repr = models.CharField(max_length=200, blank=True)
    detalhes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['modelo', 'timestamp']),
            models.Index(fields=['acao', 'timestamp']),
        ]
    
    def __str__(self):
        usuario_nome = self.usuario.get_full_name() if self.usuario else 'Sistema'
        return f"{usuario_nome} - {self.get_acao_display()} - {self.modelo} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def registrar(cls, usuario, acao, modelo, objeto=None, detalhes=None, request=None):
        """
        Método helper para registrar logs de auditoria
        """
        log = cls(
            usuario=usuario,
            acao=acao,
            modelo=modelo.__name__ if hasattr(modelo, '__name__') else str(modelo),
            detalhes=detalhes or {}
        )
        
        if objeto:
            log.objeto_id = objeto.pk if hasattr(objeto, 'pk') else None
            log.objeto_repr = str(objeto)
        
        if request:
            # Capturar IP e User-Agent do request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                log.ip_address = x_forwarded_for.split(',')[0]
            else:
                log.ip_address = request.META.get('REMOTE_ADDR')
            
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        log.save()
        return log


# Signals para criar logs automáticos
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Usuario)
def log_usuario_save(sender, instance, created, **kwargs):
    acao = 'create' if created else 'update'
    LogAuditoria.registrar(
        usuario=instance,
        acao=acao,
        modelo=sender,
        objeto=instance
    )

@receiver(post_save, sender=Agendamento)
def log_agendamento_save(sender, instance, created, **kwargs):
    acao = 'create' if created else 'update'
    LogAuditoria.registrar(
        usuario=instance.criado_por,
        acao=acao,
        modelo=sender,
        objeto=instance
    )

@receiver(post_delete, sender=Agendamento)
def log_agendamento_delete(sender, instance, **kwargs):
    LogAuditoria.registrar(
        usuario=None,  # Será definido na view
        acao='delete',
        modelo=sender,
        objeto=instance
    )
