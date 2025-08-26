#!/usr/bin/env python
"""
Script para corrigir problemas de login
Cria/atualiza usuário admin com credenciais corretas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento_sistema.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Usuario

def verificar_usuarios():
    """Verificar usuários existentes"""
    print("🔍 Verificando usuários existentes...")
    
    usuarios = Usuario.objects.all()
    
    if not usuarios.exists():
        print("❌ Nenhum usuário encontrado no banco!")
        return False
    
    print(f"✅ Total de usuários: {usuarios.count()}")
    
    for usuario in usuarios:
        print(f"   - {usuario.username} ({usuario.get_tipo_display()}) - Ativo: {usuario.ativo}")
    
    return True

def criar_usuario_admin():
    """Criar ou atualizar usuário admin"""
    print("\n👤 Criando/atualizando usuário admin...")
    
    try:
        # Tentar encontrar usuário existente
        try:
            admin_user = Usuario.objects.get(username='admin')
            print("ℹ️  Usuário admin já existe, atualizando...")
            action = "atualizado"
        except Usuario.DoesNotExist:
            admin_user = Usuario()
            admin_user.username = 'admin'
            print("✨ Criando novo usuário admin...")
            action = "criado"
        
        # Configurar dados do usuário
        admin_user.email = 'admin@sistema.com'
        admin_user.first_name = 'Administrador'
        admin_user.last_name = 'Sistema'
        admin_user.tipo = 'master'
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.ativo = True
        
        # Definir senha
        admin_user.set_password('admin123')
        
        # Salvar usuário
        admin_user.save()
        
        print(f"✅ Usuário admin {action} com sucesso!")
        print("🔑 Credenciais:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Tipo: Master")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        return False

def criar_usuarios_exemplo():
    """Criar usuários de exemplo para teste"""
    print("\n👥 Criando usuários de exemplo...")
    
    usuarios_exemplo = [
        {
            'username': 'funcionario',
            'password': 'func123',
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'funcionario@sistema.com',
            'tipo': 'restrito',
            'permissoes': {
                'pode_cadastrar_cliente': True,
                'pode_agendar': True,
                'pode_ver_agendamentos': True,
            }
        },
        {
            'username': 'cliente',
            'password': 'cliente123',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'email': 'cliente@sistema.com',
            'tipo': 'cliente',
        }
    ]
    
    for dados in usuarios_exemplo:
        try:
            # Verificar se usuário já existe
            if Usuario.objects.filter(username=dados['username']).exists():
                print(f"ℹ️  Usuário {dados['username']} já existe")
                continue
            
            # Criar usuário
            usuario = Usuario()
            usuario.username = dados['username']
            usuario.email = dados['email']
            usuario.first_name = dados['first_name']
            usuario.last_name = dados['last_name']
            usuario.tipo = dados['tipo']
            usuario.is_active = True
            usuario.ativo = True
            
            # Configurar permissões se for restrito
            if dados['tipo'] == 'restrito' and 'permissoes' in dados:
                for perm, valor in dados['permissoes'].items():
                    setattr(usuario, perm, valor)
            
            # Definir senha
            usuario.set_password(dados['password'])
            
            # Salvar
            usuario.save()
            
            print(f"✅ Usuário {dados['username']} criado!")
            
        except Exception as e:
            print(f"❌ Erro ao criar {dados['username']}: {e}")

def testar_login():
    """Testar login do usuário admin"""
    print("\n🔐 Testando login do usuário admin...")
    
    try:
        from django.contrib.auth import authenticate
        
        # Testar autenticação
        user = authenticate(username='admin', password='admin123')
        
        if user:
            print("✅ Login funcionando corretamente!")
            print(f"   - Username: {user.username}")
            print(f"   - Nome: {user.get_full_name()}")
            print(f"   - Email: {user.email}")
            print(f"   - Tipo: {user.get_tipo_display()}")
            print(f"   - Ativo: {user.ativo}")
            print(f"   - Superuser: {user.is_superuser}")
            return True
        else:
            print("❌ Falha no login!")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return False

def verificar_configuracao_django():
    """Verificar se Django está configurado corretamente"""
    print("\n⚙️ Verificando configurações Django...")
    
    try:
        from django.conf import settings
        
        # Verificar modelo de usuário
        auth_user_model = getattr(settings, 'AUTH_USER_MODEL', None)
        print(f"✅ AUTH_USER_MODEL: {auth_user_model}")
        
        if auth_user_model != 'core.Usuario':
            print("⚠️  AVISO: AUTH_USER_MODEL deve ser 'core.Usuario'")
        
        # Verificar banco de dados
        db_config = settings.DATABASES['default']
        print(f"✅ Database Engine: {db_config['ENGINE']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def executar_migracoes():
    """Executar migrações se necessário"""
    print("\n🗄️ Verificando migrações...")
    
    try:
        from django.core.management import execute_from_command_line
        import subprocess
        
        # Executar makemigrations
        print("📋 Executando makemigrations...")
        result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  Aviso makemigrations: {result.stderr}")
        
        # Executar migrate
        print("📋 Executando migrate...")
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrações aplicadas com sucesso!")
            return True
        else:
            print(f"❌ Erro nas migrações: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORRIGINDO PROBLEMAS DE LOGIN")
    print("=" * 50)
    
    # Verificar configurações
    if not verificar_configuracao_django():
        print("❌ Problema nas configurações Django")
        return False
    
    # Executar migrações
    if not executar_migracoes():
        print("⚠️  Problemas nas migrações, mas continuando...")
    
    # Verificar usuários existentes
    verificar_usuarios()
    
    # Criar usuário admin
    if not criar_usuario_admin():
        print("❌ Falha ao criar usuário admin")
        return False
    
    # Criar usuários de exemplo
    criar_usuarios_exemplo()
    
    # Testar login
    if testar_login():
        print("\n🎉 PROBLEMA DE LOGIN RESOLVIDO!")
        print("=" * 50)
        print("🔑 CREDENCIAIS CORRETAS:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🌐 Acesse: http://localhost:8000")
        print("✅ Agora o login deve funcionar!")
        return True
    else:
        print("\n❌ Login ainda não está funcionando")
        print("💡 Possíveis soluções:")
        print("   1. Reinicie o servidor Django")
        print("   2. Execute: python manage.py runserver")
        print("   3. Limpe cache do navegador")
        return False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print("💡 Certifique-se de estar na pasta do projeto Django")