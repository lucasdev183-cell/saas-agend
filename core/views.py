from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, 
    DetailView, TemplateView
)
from datetime import datetime, timedelta, date
import json

from .models import (
    Usuario, Funcionario, Cargo, Servico, 
    Agendamento, ConfiguracaoEmpresa, LogAuditoria
)
from .forms import (
    LoginForm, UsuarioForm, PermissoesUsuarioForm, CargoForm,
    FuncionarioForm, ServicoForm, AgendamentoForm, 
    ConfiguracaoEmpresaForm, FiltroAgendamentoForm
)


# Mixins personalizados
class PermissionRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar permissões granulares"""
    permission_required = None
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if self.request.user.is_master():
            return True
        
        if self.permission_required:
            return self.request.user.tem_permissao(self.permission_required)
        
        return False


# Views de Autenticação
def login_view(request):
    """View de login customizada"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Registrar log de login
            LogAuditoria.registrar(
                usuario=user,
                acao='login',
                modelo='Usuario',
                request=request
            )
            
            # Redirect para próxima página ou dashboard
            next_url = request.GET.get('next', 'core:dashboard')
            messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'core/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """View de logout"""
    usuario = request.user
    
    # Registrar log de logout
    LogAuditoria.registrar(
        usuario=usuario,
        acao='logout',
        modelo='Usuario',
        request=request
    )
    
    logout(request)
    messages.info(request, 'Logout realizado com sucesso.')
    return redirect('core:login')


# Dashboard
@login_required
def dashboard_view(request):
    """Dashboard principal com estatísticas"""
    
    # Estatísticas gerais
    total_usuarios = Usuario.objects.filter(ativo=True).count()
    total_funcionarios = Funcionario.objects.filter(ativo=True).count()
    total_clientes = Usuario.objects.filter(tipo='cliente', ativo=True).count()
    total_servicos = Servico.objects.filter(ativo=True).count()
    
    # Agendamentos de hoje
    hoje = timezone.now().date()
    agendamentos_hoje = Agendamento.objects.filter(
        data_agendamento__date=hoje
    ).count()
    
    # Próximos agendamentos (próximos 7 dias)
    proximo_semana = hoje + timedelta(days=7)
    proximos_agendamentos = Agendamento.objects.filter(
        data_agendamento__date__range=[hoje, proximo_semana],
        status='agendado'
    ).order_by('data_agendamento')[:5]
    
    # Agendamentos por status (últimos 30 dias)
    ultimo_mes = hoje - timedelta(days=30)
    agendamentos_status = Agendamento.objects.filter(
        data_agendamento__date__gte=ultimo_mes
    ).values('status').annotate(
        total=Count('id')
    ).order_by('status')
    
    # Receita do mês atual
    primeiro_dia_mes = hoje.replace(day=1)
    receita_mes = Agendamento.objects.filter(
        data_agendamento__date__gte=primeiro_dia_mes,
        status='concluido'
    ).aggregate(
        total=Sum('valor_final')
    )['total'] or 0
    
    # Dados para gráficos
    chart_data = {
        'agendamentos_por_status': list(agendamentos_status),
        'receita_mes': float(receita_mes)
    }
    
    context = {
        'total_usuarios': total_usuarios,
        'total_funcionarios': total_funcionarios,
        'total_clientes': total_clientes,
        'total_servicos': total_servicos,
        'agendamentos_hoje': agendamentos_hoje,
        'proximos_agendamentos': proximos_agendamentos,
        'receita_mes': receita_mes,
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'core/dashboard/index.html', context)


# Views de Usuários
class UsuarioListView(LoginRequiredMixin, ListView):
    """Lista de usuários"""
    model = Usuario
    template_name = 'core/usuarios/list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Usuario.objects.filter(ativo=True)
        
        # Filtros
        tipo = self.request.GET.get('tipo')
        busca = self.request.GET.get('busca')
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if busca:
            queryset = queryset.filter(
                Q(first_name__icontains=busca) |
                Q(last_name__icontains=busca) |
                Q(username__icontains=busca) |
                Q(email__icontains=busca)
            )
        
        return queryset.order_by('first_name', 'last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = Usuario.TIPO_CHOICES
        context['filtro_tipo'] = self.request.GET.get('tipo', '')
        context['busca'] = self.request.GET.get('busca', '')
        return context


class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Criação de usuários"""
    model = Usuario
    form_class = UsuarioForm
    template_name = 'core/usuarios/form.html'
    success_url = reverse_lazy('core:usuarios_list')
    permission_required = 'pode_cadastrar_cliente'  # Será verificado na view
    
    def test_func(self):
        """Verificar permissões específicas baseadas no tipo de usuário"""
        if not self.request.user.is_authenticated:
            return False
        
        if self.request.user.is_master():
            return True
        
        # Para usuários restritos, verificar baseado no tipo que está tentando criar
        tipo_usuario = self.request.POST.get('tipo', 'cliente')
        
        if tipo_usuario == 'cliente':
            return self.request.user.tem_permissao('pode_cadastrar_cliente')
        elif tipo_usuario in ['restrito', 'master']:
            return self.request.user.tem_permissao('pode_cadastrar_funcionario')
        
        return False
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario_logado'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log
        LogAuditoria.registrar(
            usuario=self.request.user,
            acao='create',
            modelo=Usuario,
            objeto=self.object,
            request=self.request
        )
        
        messages.success(
            self.request, 
            f'Usuário {self.object.get_full_name()} criado com sucesso!'
        )
        return response


class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    """Edição de usuários"""
    model = Usuario
    form_class = UsuarioForm
    template_name = 'core/usuarios/form.html'
    success_url = reverse_lazy('core:usuarios_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario_logado'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log
        LogAuditoria.registrar(
            usuario=self.request.user,
            acao='update',
            modelo=Usuario,
            objeto=self.object,
            request=self.request
        )
        
        messages.success(
            self.request, 
            f'Usuário {self.object.get_full_name()} atualizado com sucesso!'
        )
        return response


class UsuarioDetailView(LoginRequiredMixin, DetailView):
    """Detalhes do usuário"""
    model = Usuario
    template_name = 'core/usuarios/detail.html'
    context_object_name = 'usuario'


@login_required
def usuario_permissoes_view(request, pk):
    """Gerenciar permissões de usuário restrito"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Apenas masters podem alterar permissões
    if not request.user.is_master():
        messages.error(request, 'Você não tem permissão para alterar permissões.')
        return redirect('core:usuarios_list')
    
    # Apenas usuários restritos podem ter permissões alteradas
    if usuario.tipo != 'restrito':
        messages.error(request, 'Apenas usuários restritos podem ter permissões alteradas.')
        return redirect('core:usuarios_detail', pk=pk)
    
    if request.method == 'POST':
        form = PermissoesUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            
            # Registrar log
            LogAuditoria.registrar(
                usuario=request.user,
                acao='update',
                modelo=Usuario,
                objeto=usuario,
                detalhes={'acao': 'alteracao_permissoes'},
                request=request
            )
            
            messages.success(request, 'Permissões atualizadas com sucesso!')
            return redirect('core:usuarios_detail', pk=pk)
    else:
        form = PermissoesUsuarioForm(instance=usuario)
    
    return render(request, 'core/usuarios/permissoes.html', {
        'usuario': usuario,
        'form': form
    })


@login_required
def usuario_toggle_ativo(request, pk):
    """Ativar/desativar usuário"""
    if not request.user.is_master():
        messages.error(request, 'Você não tem permissão para esta ação.')
        return redirect('core:usuarios_list')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Não permitir desativar o próprio usuário
    if usuario == request.user:
        messages.error(request, 'Você não pode desativar seu próprio usuário.')
        return redirect('core:usuarios_list')
    
    usuario.ativo = not usuario.ativo
    usuario.save()
    
    status = 'ativado' if usuario.ativo else 'desativado'
    
    # Registrar log
    LogAuditoria.registrar(
        usuario=request.user,
        acao='update',
        modelo=Usuario,
        objeto=usuario,
        detalhes={'acao': f'usuario_{status}'},
        request=request
    )
    
    messages.success(request, f'Usuário {status} com sucesso!')
    return redirect('core:usuarios_list')
