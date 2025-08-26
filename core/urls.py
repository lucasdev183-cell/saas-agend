from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticação
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Usuários
    path('usuarios/', views.UsuarioListView.as_view(), name='usuarios_list'),
    path('usuarios/novo/', views.UsuarioCreateView.as_view(), name='usuarios_create'),
    path('usuarios/<int:pk>/', views.UsuarioDetailView.as_view(), name='usuarios_detail'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuarios_update'),
    path('usuarios/<int:pk>/permissoes/', views.usuario_permissoes_view, name='usuarios_permissoes'),
    path('usuarios/<int:pk>/toggle-ativo/', views.usuario_toggle_ativo, name='usuarios_toggle_ativo'),
    
    # # Cargos (serão implementados em seguida)
    # path('cargos/', views.CargoListView.as_view(), name='cargos_list'),
    # path('cargos/novo/', views.CargoCreateView.as_view(), name='cargos_create'),
    # path('cargos/<int:pk>/editar/', views.CargoUpdateView.as_view(), name='cargos_update'),
    # path('cargos/<int:pk>/deletar/', views.CargoDeleteView.as_view(), name='cargos_delete'),
    
    # # Funcionários
    # path('funcionarios/', views.FuncionarioListView.as_view(), name='funcionarios_list'),
    # path('funcionarios/novo/', views.FuncionarioCreateView.as_view(), name='funcionarios_create'),
    # path('funcionarios/<int:pk>/', views.FuncionarioDetailView.as_view(), name='funcionarios_detail'),
    # path('funcionarios/<int:pk>/editar/', views.FuncionarioUpdateView.as_view(), name='funcionarios_update'),
    
    # # Serviços
    # path('servicos/', views.ServicoListView.as_view(), name='servicos_list'),
    # path('servicos/novo/', views.ServicoCreateView.as_view(), name='servicos_create'),
    # path('servicos/<int:pk>/editar/', views.ServicoUpdateView.as_view(), name='servicos_update'),
    # path('servicos/<int:pk>/deletar/', views.ServicoDeleteView.as_view(), name='servicos_delete'),
    
    # # Agendamentos
    # path('agendamentos/', views.AgendamentoListView.as_view(), name='agendamentos_list'),
    # path('agendamentos/novo/', views.AgendamentoCreateView.as_view(), name='agendamentos_create'),
    # path('agendamentos/<int:pk>/', views.AgendamentoDetailView.as_view(), name='agendamentos_detail'),
    # path('agendamentos/<int:pk>/editar/', views.AgendamentoUpdateView.as_view(), name='agendamentos_update'),
    # path('agendamentos/<int:pk>/cancelar/', views.agendamento_cancelar, name='agendamentos_cancelar'),
    
    # # Relatórios
    # path('relatorios/', views.relatorios_view, name='relatorios'),
    # path('relatorios/agendamentos/', views.relatorio_agendamentos_view, name='relatorio_agendamentos'),
    # path('relatorios/receitas/', views.relatorio_receitas_view, name='relatorio_receitas'),
    
    # # Configurações
    # path('configuracoes/', views.ConfiguracaoEmpresaUpdateView.as_view(), name='configuracoes'),
    
    # # API endpoints (para AJAX)
    # path('api/agendamentos-calendario/', views.agendamentos_calendario_api, name='api_agendamentos_calendario'),
    # path('api/funcionarios-disponiveis/', views.funcionarios_disponiveis_api, name='api_funcionarios_disponiveis'),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)