# Sistema de Agendamento e Gestão

Sistema web de agendamento e gestão desenvolvido em Django, destinado a pequenas e médias empresas que precisam gerenciar clientes, funcionários, serviços e agendamentos. O sistema possui uma arquitetura robusta com controle de acesso baseado em papéis e funcionalidades completas de transações.

## 🚀 Tecnologias Utilizadas

### Backend
- **Framework**: Django 4.2
- **ORM**: Django ORM nativo
- **Banco de Dados**: PostgreSQL com psycopg2-binary (SQLite para desenvolvimento)
- **Autenticação**: Sistema de usuários Django customizado
- **Formulários**: Django Forms com crispy-forms
- **Validação**: Validadores Django nativos
- **Servidor**: Gunicorn para produção
- **Segurança**: Django security features + configurações personalizadas

### Frontend
- **Framework CSS**: Bootstrap 5.3.0
- **Ícones**: Font Awesome 6.4.0
- **Templates**: Django Templates (Jinja2)
- **Design**: Responsivo com sidebar colapsível
- **JavaScript**: Vanilla JS + Bootstrap JS

### Infraestrutura
- **Proxy**: Nginx para produção
- **Upload de Arquivos**: Limite de 16MB
- **Logs**: Sistema de logs integrado Django
- **Containerização**: Docker + Docker Compose

## 🏗️ Arquitetura do Sistema

### Modelos de Dados (Entidades)

- **Usuario** - Sistema central de usuários
  - Autenticação e autorização
  - Tipos: Master, Restrito e Cliente
  - Permissões granulares por funcionalidade

- **Funcionario** - Funcionários da empresa
  - Vinculado a usuários e cargos
  - Controle de dados de contratação

- **Cargo** - Posições/cargos dos funcionários
  - Gerente, Atendente, Especialista (padrão)

- **Agendamento** - Core do sistema
  - Relaciona clientes, funcionários e serviços
  - Status: agendado, concluído, cancelado

- **Servico** - Serviços oferecidos
  - Preço, duração e descrição

- **ConfiguracaoEmpresa** - Configurações da empresa
  - Logotipo, nome da empresa
  - Integração com WhatsApp (futuro)

- **LogAuditoria** - Auditoria do sistema
  - Rastreamento de ações e mudanças

### Sistema de Permissões

**Usuário Master**
- Acesso total ao sistema
- Gestão de usuários e configurações
- Acesso a todos os relatórios

**Usuário Restrito (Permissões Granulares)**
- pode_cadastrar_cliente
- pode_cadastrar_funcionario
- pode_cadastrar_cargo
- pode_agendar
- pode_ver_agendamentos
- pode_ver_relatorios

## ⚡ Funcionalidades Principais

### 1. Dashboard
- Estatísticas gerais do sistema
- Total de usuários, funcionários, agendamentos
- Agendamentos do dia e próximos

### 2. Gestão de Usuários
- Cadastro, edição e visualização
- Sistema de permissões granulares
- Usuários master e restritos
- Clientes sem necessidade de senha

### 3. Gestão de Funcionários
- Vinculação com usuários e cargos
- Controle de funcionários ativos
- Dados de contratação

### 4. Gestão de Cargos
- Criação e edição de cargos
- Verificação de referências antes da exclusão

### 5. Gestão de Serviços
- Cadastro de serviços oferecidos
- Preço e duração configuráveis
- Controle de serviços ativos

### 6. Sistema de Agendamentos
- Agendamento entre clientes e funcionários
- Seleção de funcionários e serviços
- Atualização de status dos agendamentos
- Observações e durações personalizáveis

### 7. Relatórios (Em desenvolvimento)
- Agendamentos por período
- Estatísticas de funcionários
- Relatórios de clientes

### 8. Configurações da Empresa
- Upload de logotipo da empresa
- Configuração do nome da empresa
- Configurações de WhatsApp

### 9. Bot WhatsApp (Em desenvolvimento)
- Configuração de tokens
- Webhook para recebimento de mensagens
- Fluxo de atendimento

## 🔒 Recursos de Segurança

- **Autenticação**: Hash de senhas com Django
- **Sessões**: Gestão segura com Django
- **Validações**: Integridade referencial no banco
- **Upload Seguro**: Validação de arquivos e tamanhos seguros
- **Logs de Auditoria**: Rastreamento de ações dos usuários
- **CSRF Protection**: Proteção contra ataques CSRF
- **Headers de Segurança**: X-Frame-Options, Content Security Policy

## 📱 Interface e UX

- **Design Responsivo**: Compatível com mobile e desktop
- **Sidebar Dinâmica**: Menu lateral com permissões contextuais
- **Formulários Inteligentes**: Validação em tempo real
- **Feedback Visual**: Mensagens de sucesso/erro
- **Pesquisa Avançada**: Filtros para usuários, clientes e funcionários

## 🗄️ Banco de Dados

- **PostgreSQL** como SGBD principal
- **Migrações**: Sistema de migrações Django automáticas
- **Pool de Conexões**: Configuração otimizada
- **Integridade**: Verificação de referências antes de exclusões

## 🚀 Instalação e Deploy

### Desenvolvimento Local

#### **Instalação Automática (Recomendado)**

**Windows:**
```batch
# 1. Execute o instalador completo (instala tudo + configura banco + inicia servidor)
install.bat

# OU faça por etapas:
# 2a. Configurar banco de dados
python database_setup.py

# 2b. Iniciar servidor
python start_server.py
```

**Linux/Mac:**
```bash
# 1. Execute o instalador automático
python install.py

# 2. Configure o banco de dados
python database_setup.py

# 3. Inicie o servidor
python start_server.py
```

#### **Instalação Manual**

1. **Clone o repositório**
```bash
git clone https://github.com/lucasdev183-cell/saas-agend
cd saas-agend
```

2. **Criar ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instalar dependências uma por uma (se der erro)**
```bash
pip install --upgrade pip
pip install django==4.2
pip install psycopg2-binary==2.9.10
pip install pillow==11.3.0
pip install python-decouple==3.8
pip install django-crispy-forms==2.1
pip install crispy-bootstrap5==0.7
pip install django-widget-tweaks==1.5.0
pip install whitenoise==6.6.0
pip install gunicorn==21.2.0
pip install django-extensions==4.1
```

4. **Executar migrações**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Criar superusuário**
```bash
python manage.py createsuperuser
```

6. **Executar servidor**
```bash
python manage.py runserver
```

### Deploy com Docker

1. **Build e execução**
```bash
docker-compose up -d
```

2. **Executar migrações**
```bash
docker-compose exec web python manage.py migrate
```

3. **Criar superusuário**
```bash
docker-compose exec web python manage.py createsuperuser
```

### Deploy em Produção

1. **Configurar variáveis de ambiente**
```bash
export DEBUG=False
export SECRET_KEY=your-secret-key
export DB_HOST=your-db-host
export DB_PASSWORD=your-db-password
```

2. **Executar com Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Variáveis de Ambiente

```env
# Configurações de Desenvolvimento
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados
USE_SQLITE=True  # Para desenvolvimento
PGDATABASE=db_sa
PGUSER=postgres
PGPASSWORD=xbala
PGHOST=localhost
PGPORT=5432

# Email (futuro)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# WhatsApp Bot (futuro)
WHATSAPP_TOKEN=
WHATSAPP_WEBHOOK_VERIFY_TOKEN=
```

## 🔧 Comandos Úteis

```bash
# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Acessar shell Django
python manage.py shell

# Criar dados de exemplo
python manage.py loaddata fixtures/example_data.json
```

## 📊 Logs

Os logs são salvos no diretório `logs/` e incluem:
- Logs de aplicação Django
- Logs de auditoria do sistema
- Logs de erros e debugging

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Entre em contato via email: admin@exemplo.com

## 🎯 Roadmap

- [ ] Sistema completo de relatórios
- [ ] Integração com WhatsApp Bot
- [ ] API REST para integração externa
- [ ] Sistema de notificações
- [ ] Agenda visual (calendário)
- [ ] Integração com sistemas de pagamento
- [ ] App mobile (React Native)

## 📋 Credenciais de Teste

**Usuário Master:**
- Username: admin
- Password: admin123

**Usuário Restrito:**
- Username: funcionario
- Password: func123

---

Desenvolvido com ❤️ por [Seu Nome]