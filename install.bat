@echo off
echo.
echo ================================================
echo 🚀 Sistema de Agendamento - Instalacao Windows
echo ================================================
echo.

echo 📦 Atualizando pip...
python -m pip install --upgrade pip

echo.
echo 📦 Instalando dependencias essenciais...

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

echo.
echo 🗄️ Configurando banco de dados...
python manage.py makemigrations
python manage.py migrate

echo.
echo 👤 Criando usuario admin...
echo from core.models import Usuario; Usuario.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'tipo': 'master', 'is_superuser': True, 'is_staff': True}); u = Usuario.objects.get(username='admin'); u.set_password('admin123'); u.save(); print('Usuario admin criado/atualizado!') | python manage.py shell

echo.
echo ✅ Instalacao concluida!
echo ================================================
echo 🚀 Opcoes para continuar:
echo.
echo 1. Setup do banco de dados:
echo    python database_setup.py
echo.
echo 2. Iniciar servidor:
echo    python start_server.py
echo.
echo 🔑 Credenciais de acesso:
echo    Usuario: admin
echo    Senha: admin123
echo.
echo 🌐 Acesse: http://localhost:8000
echo ================================================

echo.
echo 🗄️ Configurando banco de dados automaticamente...
python database_setup.py

echo.
echo 🔧 Corrigindo problemas de login...
python corrigir_login.py

echo.
echo 🚀 Deseja iniciar o servidor agora? (S/N)
set /p choice=Digite sua escolha: 
if /i "%choice%"=="S" (
    python start_server.py
) else (
    echo.
    echo ✅ Setup concluido! Execute 'python start_server.py' quando quiser iniciar.
    pause
)