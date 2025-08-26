#!/usr/bin/env python
"""
Script de diagnóstico completo para problemas de conexão
Sistema de Agendamento e Gestão
"""
import os
import sys
import subprocess
import socket
import platform
import time

def print_header(title):
    """Imprimir cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def check_python_version():
    """Verificar versão do Python"""
    print_header("VERIFICANDO PYTHON")
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  AVISO: Python 3.8+ é recomendado para Django 4.2")
    
    return True

def check_django_installation():
    """Verificar se Django está instalado"""
    print_header("VERIFICANDO DJANGO")
    try:
        import django
        print(f"✅ Django {django.get_version()} instalado")
        
        # Verificar se manage.py existe
        if os.path.exists('manage.py'):
            print("✅ manage.py encontrado")
        else:
            print("❌ manage.py NÃO encontrado!")
            return False
            
        return True
    except ImportError:
        print("❌ Django NÃO instalado!")
        print("💡 Execute: pip install django==4.2")
        return False

def check_dependencies():
    """Verificar dependências críticas"""
    print_header("VERIFICANDO DEPENDÊNCIAS")
    
    dependencies = [
        ('django', 'Django'),
        ('psycopg2', 'PostgreSQL driver'),
        ('PIL', 'Pillow (imagens)'),
        ('decouple', 'python-decouple'),
        ('crispy_forms', 'django-crispy-forms'),
        ('crispy_bootstrap5', 'crispy-bootstrap5'),
        ('widget_tweaks', 'django-widget-tweaks')
    ]
    
    missing = []
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - FALTANDO!")
            missing.append(module)
    
    if missing:
        print(f"\n💡 Para instalar dependências faltantes:")
        for module in missing:
            if module == 'PIL':
                print(f"   pip install pillow")
            elif module == 'psycopg2':
                print(f"   pip install psycopg2-binary")
            elif module == 'decouple':
                print(f"   pip install python-decouple")
            else:
                print(f"   pip install {module}")
        return False
    
    return True

def check_port_usage():
    """Verificar uso da porta 8000"""
    print_header("VERIFICANDO PORTA 8000")
    
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    if is_port_open(8000):
        print("⚠️  Porta 8000 está OCUPADA!")
        
        # Tentar identificar o processo
        system = platform.system()
        try:
            if system == "Windows":
                result = subprocess.run('netstat -ano | findstr :8000', 
                                      shell=True, capture_output=True, text=True)
                if result.stdout:
                    print("📋 Processos usando porta 8000:")
                    print(result.stdout)
            else:
                result = subprocess.run('lsof -i:8000', 
                                      shell=True, capture_output=True, text=True)
                if result.stdout:
                    print("📋 Processos usando porta 8000:")
                    print(result.stdout)
        except:
            pass
            
        print("\n💡 Para liberar a porta:")
        if system == "Windows":
            print("   1. Abra o Gerenciador de Tarefas")
            print("   2. Finalize processos 'python.exe' ou 'runserver'")
            print("   3. OU execute: taskkill /F /IM python.exe")
        else:
            print("   sudo lsof -ti:8000 | xargs kill -9")
            
        return False
    else:
        print("✅ Porta 8000 está LIVRE!")
        return True

def check_django_settings():
    """Verificar configurações Django"""
    print_header("VERIFICANDO CONFIGURAÇÕES DJANGO")
    
    try:
        # Verificar se consegue importar settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento_sistema.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        print("✅ Settings Django carregado com sucesso!")
        print(f"✅ DEBUG = {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
        
        # Verificar banco de dados
        db_config = settings.DATABASES['default']
        print(f"✅ Database ENGINE = {db_config['ENGINE']}")
        
        if 'sqlite3' in db_config['ENGINE']:
            print(f"✅ Database FILE = {db_config['NAME']}")
        else:
            print(f"✅ Database HOST = {db_config.get('HOST', 'N/A')}")
            print(f"✅ Database NAME = {db_config.get('NAME', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar configurações Django: {e}")
        return False

def check_database_connection():
    """Verificar conexão com banco de dados"""
    print_header("VERIFICANDO BANCO DE DADOS")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento_sistema.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        
        # Testar conexão
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        print("✅ Conexão com banco de dados OK!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        print("\n💡 Possíveis soluções:")
        print("   1. Execute: python database_setup.py")
        print("   2. Verifique se PostgreSQL está rodando")
        print("   3. Verifique credenciais no .env")
        return False

def test_django_server():
    """Testar se consegue iniciar servidor Django"""
    print_header("TESTANDO SERVIDOR DJANGO")
    
    try:
        # Tentar executar check do Django
        result = subprocess.run([sys.executable, 'manage.py', 'check'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Django check passou!")
            print("✅ Servidor Django deve funcionar!")
            return True
        else:
            print("❌ Django check falhou:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout no Django check")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar Django: {e}")
        return False

def test_simple_server():
    """Iniciar um servidor simples para testar conectividade"""
    print_header("TESTE DE SERVIDOR SIMPLES")
    
    try:
        import http.server
        import socketserver
        import threading
        
        print("🚀 Iniciando servidor simples na porta 8001...")
        
        class SimpleHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Servidor funcionando!</h1>')
        
        httpd = socketserver.TCPServer(("", 8001), SimpleHandler)
        
        # Iniciar em thread separada
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        time.sleep(2)
        
        # Testar conectividade
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8001))
        sock.close()
        
        httpd.shutdown()
        
        if result == 0:
            print("✅ Servidor simples funcionou!")
            print("✅ Conectividade de rede OK!")
            print("🌐 Teste: http://localhost:8001")
            return True
        else:
            print("❌ Falha na conectividade local")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de servidor: {e}")
        return False

def provide_solutions():
    """Fornecer soluções baseadas nos problemas encontrados"""
    print_header("SOLUÇÕES RECOMENDADAS")
    
    print("🔧 Execute os comandos na seguinte ordem:")
    print()
    print("1️⃣ INSTALAR DEPENDÊNCIAS:")
    print("   pip install --upgrade pip")
    print("   pip install django==4.2")
    print("   pip install psycopg2-binary")
    print("   pip install pillow")
    print("   pip install python-decouple")
    print("   pip install django-crispy-forms")
    print("   pip install crispy-bootstrap5")
    print("   pip install django-widget-tweaks")
    print()
    print("2️⃣ CONFIGURAR BANCO:")
    print("   python database_setup.py")
    print()
    print("3️⃣ EXECUTAR MIGRAÇÕES:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print()
    print("4️⃣ INICIAR SERVIDOR:")
    print("   python manage.py runserver 0.0.0.0:8000")
    print()
    print("5️⃣ TESTAR CONECTIVIDADE:")
    print("   Abra: http://localhost:8000")
    print("   OU: http://127.0.0.1:8000")
    print()
    print("💡 Se ainda não funcionar:")
    print("   - Reinicie o computador")
    print("   - Desative temporariamente antivírus/firewall")
    print("   - Tente porta diferente: python manage.py runserver 8080")

def main():
    """Função principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA")
    print("🎯 Identificando problemas de conexão Django")
    
    # Lista de verificações
    checks = [
        ("Python", check_python_version),
        ("Django", check_django_installation),
        ("Dependências", check_dependencies),
        ("Porta 8000", check_port_usage),
        ("Configurações", check_django_settings),
        ("Banco de Dados", check_database_connection),
        ("Servidor Django", test_django_server),
        ("Conectividade", test_simple_server)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except KeyboardInterrupt:
            print("\n🛑 Diagnóstico interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro inesperado em {name}: {e}")
            results[name] = False
    
    # Resumo final
    print_header("RESUMO DO DIAGNÓSTICO")
    
    for name, result in results.items():
        status = "✅ OK" if result else "❌ PROBLEMA"
        print(f"{status} {name}")
    
    failed = [name for name, result in results.items() if not result]
    
    if failed:
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS: {', '.join(failed)}")
        provide_solutions()
    else:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 O servidor deve funcionar normalmente!")
        print("💡 Execute: python manage.py runserver")

if __name__ == "__main__":
    main()