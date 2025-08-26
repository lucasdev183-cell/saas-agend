#!/usr/bin/env python
"""
Script para iniciar o servidor Django com verificações automáticas
Sistema de Agendamento e Gestão
"""
import os
import sys
import subprocess
import time
import socket

def check_port(port):
    """Verificar se uma porta está disponível"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True se porta está livre

def kill_process_on_port(port):
    """Matar processo que está usando uma porta específica"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LISTENING' in line:
                        pid = line.split()[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        print(f"✅ Processo PID {pid} finalizado na porta {port}")
        else:  # Linux/Mac
            result = subprocess.run(f'lsof -ti:{port}', shell=True, capture_output=True, text=True)
            if result.stdout:
                pid = result.stdout.strip()
                subprocess.run(f'kill -9 {pid}', shell=True)
                print(f"✅ Processo PID {pid} finalizado na porta {port}")
        
        time.sleep(2)  # Aguardar processo finalizar
        return True
    except Exception as e:
        print(f"⚠️  Erro ao finalizar processo na porta {port}: {e}")
        return False

def check_django_setup():
    """Verificar se Django está configurado corretamente"""
    print("🔍 Verificando configuração Django...")
    
    # Verificar se manage.py existe
    if not os.path.exists('manage.py'):
        print("❌ Arquivo manage.py não encontrado!")
        return False
    
    # Verificar se core app existe
    if not os.path.exists('core'):
        print("❌ App 'core' não encontrado!")
        return False
    
    # Verificar se arquivo de migração existe
    if not os.path.exists('core/migrations'):
        print("⚠️  Pasta migrations não encontrada, criando...")
        os.makedirs('core/migrations', exist_ok=True)
        
        # Criar __init__.py
        with open('core/migrations/__init__.py', 'w') as f:
            f.write('')
    
    print("✅ Configuração Django OK!")
    return True

def run_migrations():
    """Executar migrações Django"""
    print("🗄️ Executando migrações...")
    
    try:
        # Fazer migrações
        result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️  Aviso makemigrations: {result.stderr}")
        
        # Aplicar migrações
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

def start_server(port=8000):
    """Iniciar servidor Django"""
    print(f"🚀 Iniciando servidor na porta {port}...")
    
    try:
        # Comando para iniciar servidor
        cmd = [sys.executable, 'manage.py', 'runserver', f'0.0.0.0:{port}']
        
        print("=" * 60)
        print("🌐 Servidor Django iniciado!")
        print(f"📍 Acesse: http://localhost:{port}")
        print("🔑 Credenciais: admin / admin123")
        print("⌨️  Pressione Ctrl+C para parar o servidor")
        print("=" * 60)
        
        # Iniciar servidor (vai rodar até ser interrompido)
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def main():
    """Função principal"""
    print("🚀 Sistema de Agendamento - Inicialização do Servidor")
    print("=" * 60)
    
    # Verificar configuração Django
    if not check_django_setup():
        print("❌ Falha na verificação Django")
        return False
    
    # Verificar porta 8000
    port = 8000
    if not check_port(port):
        print(f"⚠️  Porta {port} está em uso. Tentando liberar...")
        if not kill_process_on_port(port):
            print(f"❌ Não foi possível liberar a porta {port}")
            print("💡 Tente usar uma porta diferente ou reiniciar o computador")
            return False
    
    # Executar migrações
    if not run_migrations():
        print("⚠️  Erro nas migrações, mas continuando...")
    
    # Iniciar servidor
    start_server(port)
    
    return True

if __name__ == "__main__":
    main()