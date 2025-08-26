from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date
from .models import (
    Usuario, Funcionario, Cargo, Servico, 
    Agendamento, ConfiguracaoEmpresa
)


class LoginForm(AuthenticationForm):
    """Formulário customizado de login"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuário ou email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        })
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Tentar autenticar por username ou email
            user = authenticate(username=username, password=password)
            if not user:
                # Tentar por email
                try:
                    usuario_obj = Usuario.objects.get(email=username)
                    user = authenticate(username=usuario_obj.username, password=password)
                except Usuario.DoesNotExist:
                    pass
            
            if not user:
                raise ValidationError('Usuário ou senha inválidos.')
            elif not user.ativo:
                raise ValidationError('Usuário inativo.')
            
            self.user_cache = user
        
        return self.cleaned_data


class UsuarioForm(UserCreationForm):
    """Formulário para criação e edição de usuários"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email', 'tipo',
            'telefone', 'cpf', 'data_nascimento', 'endereco', 'foto_perfil'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        self.usuario_logado = kwargs.pop('usuario_logado', None)
        super().__init__(*args, **kwargs)
        
        # Se é edição, remover campos de senha
        if self.instance.pk:
            del self.fields['password1']
            del self.fields['password2']
        else:
            self.fields['password1'].widget.attrs['class'] = 'form-control'
            self.fields['password2'].widget.attrs['class'] = 'form-control'
        
        # Se não é master, limitar tipos de usuário
        if self.usuario_logado and not self.usuario_logado.is_master():
            self.fields['tipo'].choices = [
                ('cliente', 'Cliente'),
                ('restrito', 'Restrito')
            ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este email já está em uso.')
        return email
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf and Usuario.objects.filter(cpf=cpf).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este CPF já está em uso.')
        return cpf


class PermissoesUsuarioForm(forms.ModelForm):
    """Formulário específico para gerenciar permissões de usuários restritos"""
    
    class Meta:
        model = Usuario
        fields = [
            'pode_cadastrar_cliente', 'pode_cadastrar_funcionario',
            'pode_cadastrar_cargo', 'pode_agendar',
            'pode_ver_agendamentos', 'pode_ver_relatorios'
        ]
        widgets = {
            'pode_cadastrar_cliente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_cadastrar_funcionario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_cadastrar_cargo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_agendar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_ver_agendamentos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_ver_relatorios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CargoForm(forms.ModelForm):
    """Formulário para criação e edição de cargos"""
    
    class Meta:
        model = Cargo
        fields = ['nome', 'descricao', 'salario_base', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'salario_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if Cargo.objects.filter(nome=nome).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Já existe um cargo com este nome.')
        return nome


class FuncionarioForm(forms.ModelForm):
    """Formulário para criação e edição de funcionários"""
    
    class Meta:
        model = Funcionario
        fields = [
            'usuario', 'cargo', 'data_contratacao', 'data_demissao',
            'salario', 'observacoes', 'ativo'
        ]
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'cargo': forms.Select(attrs={'class': 'form-select'}),
            'data_contratacao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_demissao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'salario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas usuários que não são funcionários ou o próprio se editando
        usuarios_funcionarios = Funcionario.objects.values_list('usuario_id', flat=True)
        queryset = Usuario.objects.filter(tipo__in=['restrito', 'master'])
        
        if self.instance.pk:
            # Se editando, incluir o usuário atual
            queryset = queryset.exclude(id__in=usuarios_funcionarios).exclude(id=self.instance.usuario_id) | \
                      Usuario.objects.filter(id=self.instance.usuario_id)
        else:
            queryset = queryset.exclude(id__in=usuarios_funcionarios)
        
        self.fields['usuario'].queryset = queryset
        self.fields['cargo'].queryset = Cargo.objects.filter(ativo=True)
    
    def clean_data_contratacao(self):
        data_contratacao = self.cleaned_data.get('data_contratacao')
        if data_contratacao and data_contratacao > date.today():
            raise ValidationError('Data de contratação não pode ser no futuro.')
        return data_contratacao
    
    def clean(self):
        cleaned_data = super().clean()
        data_contratacao = cleaned_data.get('data_contratacao')
        data_demissao = cleaned_data.get('data_demissao')
        
        if data_contratacao and data_demissao:
            if data_demissao <= data_contratacao:
                raise ValidationError('Data de demissão deve ser posterior à data de contratação.')
        
        return cleaned_data


class ServicoForm(forms.ModelForm):
    """Formulário para criação e edição de serviços"""
    
    class Meta:
        model = Servico
        fields = ['nome', 'descricao', 'preco', 'duracao_minutos', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'duracao_minutos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '1440'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class AgendamentoForm(forms.ModelForm):
    """Formulário para criação e edição de agendamentos"""
    
    class Meta:
        model = Agendamento
        fields = [
            'cliente', 'funcionario', 'servico', 'data_agendamento',
            'status', 'observacoes', 'valor_final'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'funcionario': forms.Select(attrs={'class': 'form-select'}),
            'servico': forms.Select(attrs={'class': 'form-select'}),
            'data_agendamento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'valor_final': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas clientes ativos
        self.fields['cliente'].queryset = Usuario.objects.filter(
            tipo='cliente', ativo=True
        )
        
        # Filtrar apenas funcionários ativos
        self.fields['funcionario'].queryset = Funcionario.objects.filter(
            ativo=True, data_demissao__isnull=True
        )
        
        # Filtrar apenas serviços ativos
        self.fields['servico'].queryset = Servico.objects.filter(ativo=True)
    
    def clean_data_agendamento(self):
        data_agendamento = self.cleaned_data.get('data_agendamento')
        
        if data_agendamento:
            # Verificar se não é no passado (apenas para novos agendamentos)
            if not self.instance.pk and data_agendamento <= timezone.now():
                raise ValidationError('Data de agendamento deve ser no futuro.')
            
            # Verificar horário comercial (8h às 18h)
            if data_agendamento.hour < 8 or data_agendamento.hour >= 18:
                raise ValidationError('Agendamentos devem ser entre 08:00 e 18:00.')
            
            # Verificar dias úteis (segunda a sexta)
            if data_agendamento.weekday() >= 5:  # 5=sábado, 6=domingo
                raise ValidationError('Agendamentos apenas em dias úteis (segunda a sexta).')
        
        return data_agendamento
    
    def clean(self):
        cleaned_data = super().clean()
        funcionario = cleaned_data.get('funcionario')
        data_agendamento = cleaned_data.get('data_agendamento')
        servico = cleaned_data.get('servico')
        
        if funcionario and data_agendamento and servico:
            # Verificar conflito de horários
            from datetime import timedelta
            data_fim = data_agendamento + timedelta(minutes=servico.duracao_minutos)
            
            conflitos = Agendamento.objects.filter(
                funcionario=funcionario,
                data_agendamento__lt=data_fim,
                status__in=['agendado', 'em_andamento']
            ).exclude(pk=self.instance.pk)
            
            for agendamento in conflitos:
                agendamento_fim = agendamento.data_hora_fim()
                if data_agendamento < agendamento_fim:
                    raise ValidationError(
                        f'Conflito de horário com agendamento: {agendamento}'
                    )
        
        return cleaned_data


class ConfiguracaoEmpresaForm(forms.ModelForm):
    """Formulário para configurações da empresa"""
    
    class Meta:
        model = ConfiguracaoEmpresa
        fields = [
            'nome_empresa', 'logotipo', 'endereco', 'telefone', 'email', 'site',
            'whatsapp_numero', 'whatsapp_token', 'whatsapp_ativo',
            'mensagem_boas_vindas', 'horario_funcionamento'
        ]
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'logotipo': forms.FileInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'site': forms.URLInput(attrs={'class': 'form-control'}),
            'whatsapp_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_token': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mensagem_boas_vindas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'horario_funcionamento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }


class FiltroAgendamentoForm(forms.Form):
    """Formulário para filtrar agendamentos"""
    
    STATUS_CHOICES = [('', 'Todos')] + Agendamento.STATUS_CHOICES
    
    cliente = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(tipo='cliente'),
        required=False,
        empty_label='Todos os clientes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    funcionario = forms.ModelChoiceField(
        queryset=Funcionario.objects.filter(ativo=True),
        required=False,
        empty_label='Todos os funcionários',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    servico = forms.ModelChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        required=False,
        empty_label='Todos os serviços',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )