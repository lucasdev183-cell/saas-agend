#!/usr/bin/env python
"""
Script de instalação para o Sistema de Agendamento
Este script instala todas as dependências necessárias
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e mostra o progresso"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Concluído!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Sistema de Agendamento - Instalação Automática")
    print("=" * 50)
    
    # Lista de dependências essenciais
    dependencies = [
        "django==4.2",
        "psycopg2-binary==2.9.10", 
        "pillow==11.3.0",
        "python-decouple==3.8",
        "django-crispy-forms==2.1",
        "crispy-bootstrap5==0.7",
        "django-widget-tweaks==1.5.0",
        "whitenoise==6.6.0",
        "gunicorn==21.2.0",
        "django-extensions==4.1"
    ]
    
    print("📦 Instalando dependências individuais...")
    
    failed_packages = []
    for package in dependencies:
        if not run_command(f"pip install {package}", f"Instalando {package}"):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Pacotes que falharam: {failed_packages}")
        print("Tentando instalar novamente com --upgrade...")
        
        for package in failed_packages:
            run_command(f"pip install --upgrade {package}", f"Reinstalando {package}")
    
    # Verificar se Django está instalado
    try:
        import django
        print(f"✅ Django {django.get_version()} instalado com sucesso!")
    except ImportError:
        print("❌ Django não foi instalado corretamente")
        return False
    
    # Executar migrações
    print("\n🗄️  Configurando banco de dados...")
    
    if run_command("python manage.py makemigrations", "Criando migrações"):
        run_command("python manage.py migrate", "Aplicando migrações")
    
    # Criar superusuário se não existir
    print("\n👤 Verificando usuário admin...")
    create_user_script = '''
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123", tipo="master")
    print("✅ Usuário admin criado!")
else:
    print("ℹ️  Usuário admin já existe")
'''
    
    with open('create_admin.py', 'w') as f:
        f.write(create_user_script)
    
    run_command("python manage.py shell < create_admin.py", "Criando usuário admin")
    
    # Limpar arquivo temporário
    if os.path.exists('create_admin.py'):
        os.remove('create_admin.py')
    
    print("\n🎉 Instalação concluída!")
    print("=" * 50)
    print("🚀 Para iniciar o servidor:")
    print("   python manage.py runserver")
    print("\n🔑 Credenciais de acesso:")
    print("   Usuário: admin")
    print("   Senha: admin123")
    print("\n🌐 Acesse: http://localhost:8000")

if __name__ == "__main__":
    main()