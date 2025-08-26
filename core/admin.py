from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Usuario, Funcionario, Cargo, Servico, 
    Agendamento, ConfiguracaoEmpresa, LogAuditoria
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin customizado para modelo Usuario"""
    
    list_display = [
        'username', 'get_full_name', 'email', 'tipo', 
        'ativo', 'data_criacao', 'foto_perfil_thumbnail'
    ]
    list_filter = ['tipo', 'ativo', 'data_criacao', 'is_staff', 'is_superuser']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'cpf']
    ordering = ['-data_criacao']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {
            'fields': ('tipo', 'telefone', 'cpf', 'data_nascimento', 'endereco', 'foto_perfil')
        }),
        ('Permissões Granulares', {
            'fields': (
                'pode_cadastrar_cliente', 'pode_cadastrar_funcionario', 
                'pode_cadastrar_cargo', 'pode_agendar', 
                'pode_ver_agendamentos', 'pode_ver_relatorios'
            ),
            'classes': ['collapse']
        }),
        ('Controle', {
            'fields': ('ativo', 'data_criacao', 'data_atualizacao'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    def foto_perfil_thumbnail(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.foto_perfil.url
            )
        return "Sem foto"
    foto_perfil_thumbnail.short_description = "Foto"


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    """Admin para modelo Cargo"""
    
    list_display = ['nome', 'salario_base', 'ativo', 'total_funcionarios', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    
    readonly_fields = ['data_criacao']
    
    def total_funcionarios(self, obj):
        return obj.funcionario_set.count()
    total_funcionarios.short_description = "Funcionários"


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    """Admin para modelo Funcionario"""
    
    list_display = [
        'codigo_funcionario', 'usuario', 'cargo', 
        'data_contratacao', 'salario', 'ativo'
    ]
    list_filter = ['cargo', 'ativo', 'data_contratacao']
    search_fields = [
        'codigo_funcionario', 'usuario__first_name', 
        'usuario__last_name', 'cargo__nome'
    ]
    ordering = ['-data_contratacao']
    
    readonly_fields = ['codigo_funcionario', 'data_criacao']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['usuario', 'cargo', 'codigo_funcionario']
        }),
        ('Dados de Contratação', {
            'fields': ['data_contratacao', 'data_demissao', 'salario']
        }),
        ('Observações', {
            'fields': ['observacoes', 'ativo'],
            'classes': ['collapse']
        }),
        ('Controle', {
            'fields': ['data_criacao'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    """Admin para modelo Servico"""
    
    list_display = ['nome', 'preco', 'duracao_formatada', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    
    readonly_fields = ['data_criacao']
    
    fieldsets = [
        ('Informações do Serviço', {
            'fields': ['nome', 'descricao', 'ativo']
        }),
        ('Valores', {
            'fields': ['preco', 'duracao_minutos']
        }),
        ('Controle', {
            'fields': ['data_criacao'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    """Admin para modelo Agendamento"""
    
    list_display = [
        'cliente', 'funcionario', 'servico', 
        'data_agendamento', 'status', 'valor_final'
    ]
    list_filter = ['status', 'data_agendamento', 'servico', 'funcionario']
    search_fields = [
        'cliente__first_name', 'cliente__last_name',
        'funcionario__usuario__first_name', 'funcionario__usuario__last_name',
        'servico__nome'
    ]
    ordering = ['-data_agendamento']
    
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = [
        ('Agendamento', {
            'fields': ['cliente', 'funcionario', 'servico', 'data_agendamento']
        }),
        ('Status e Valores', {
            'fields': ['status', 'valor_final']
        }),
        ('Observações', {
            'fields': ['observacoes'],
            'classes': ['collapse']
        }),
        ('Controle', {
            'fields': ['criado_por', 'data_criacao', 'data_atualizacao'],
            'classes': ['collapse']
        }),
    ]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Novo agendamento
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(ConfiguracaoEmpresa)
class ConfiguracaoEmpresaAdmin(admin.ModelAdmin):
    """Admin para configurações da empresa (Singleton)"""
    
    def has_add_permission(self, request):
        # Permitir adicionar apenas se não existe nenhuma configuração
        return not ConfiguracaoEmpresa.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Nunca permitir deletar configurações da empresa
        return False
    
    fieldsets = [
        ('Informações da Empresa', {
            'fields': ['nome_empresa', 'logotipo', 'endereco', 'telefone', 'email', 'site']
        }),
        ('WhatsApp', {
            'fields': ['whatsapp_numero', 'whatsapp_token', 'whatsapp_ativo'],
            'classes': ['collapse']
        }),
        ('Configurações Gerais', {
            'fields': ['mensagem_boas_vindas', 'horario_funcionamento']
        }),
        ('Controle', {
            'fields': ['data_atualizacao'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['data_atualizacao']


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Admin para logs de auditoria (apenas leitura)"""
    
    list_display = [
        'timestamp', 'usuario', 'acao', 'modelo', 
        'objeto_repr', 'ip_address'
    ]
    list_filter = ['acao', 'modelo', 'timestamp']
    search_fields = [
        'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'modelo', 'objeto_repr', 'ip_address'
    ]
    ordering = ['-timestamp']
    
    readonly_fields = [
        'usuario', 'acao', 'modelo', 'objeto_id', 'objeto_repr',
        'detalhes', 'ip_address', 'user_agent', 'timestamp'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Customizar título do admin
admin.site.site_header = 'Sistema de Agendamento - Administração'
admin.site.site_title = 'Agendamento Admin'
admin.site.index_title = 'Painel de Controle'
