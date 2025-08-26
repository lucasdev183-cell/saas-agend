#!/usr/bin/env python
"""
Script para forçar o servidor Django a funcionar
Resolve problemas de conectividade e porta ocupada
"""
import os
import sys
import subprocess
import socket
import time
import platform

def kill_all_python():
    """Finalizar todos os processos Python para liberar portas"""
    print("🔄 Finalizando processos Python anteriores...")
    
    system = platform.system()
    try:
        if system == "Windows":
            # Windows
            subprocess.run('taskkill /F /IM python.exe', shell=True, capture_output=True)
            subprocess.run('taskkill /F /IM pythonw.exe', shell=True, capture_output=True)
            print("✅ Processos Python finalizados (Windows)")
        else:
            # Linux/Mac
            subprocess.run('pkill -f python', shell=True, capture_output=True)
            subprocess.run('pkill -f runserver', shell=True, capture_output=True)
            print("✅ Processos Python finalizados (Linux/Mac)")
            
        time.sleep(2)  # Aguardar processos finalizarem
        
    except Exception as e:
        print(f"⚠️  Aviso ao finalizar processos: {e}")

def test_port(port):
    """Testar se porta está livre"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True = livre, False = ocupada

def find_free_port():
    """Encontrar uma porta livre entre 8000-8010"""
    for port in range(8000, 8011):
        if test_port(port):
            print(f"✅ Porta {port} está livre!")
            return port
    
    print("⚠️  Nenhuma porta livre encontrada entre 8000-8010")
    return 8000  # Usar 8000 mesmo assim

def create_minimal_server():
    """Criar um servidor mínimo se Django não funcionar"""
    print("🚀 Criando servidor mínimo de backup...")
    
    server_code = '''
import http.server
import socketserver
import webbrowser
import time

PORT = 8000

html_content = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Agendamento - Servidor Temporário</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { text-align: center; background: #f8f9fa; padding: 30px; border-radius: 10px; }
        .title { color: #0d6efd; margin-bottom: 20px; }
        .message { color: #666; line-height: 1.6; }
        .button { background: #0d6efd; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 10px; cursor: pointer; }
        .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🚀 Sistema de Agendamento</h1>
        <div class="status">
            ✅ Servidor funcionando na porta ''' + str(PORT) + '''!
        </div>
        <div class="message">
            <h3>🔧 Status do Sistema:</h3>
            <p>Este é um servidor temporário para testar a conectividade.</p>
            <p>O servidor Django principal deve estar funcionando.</p>
            
            <h3>📋 Próximos Passos:</h3>
            <p>1. Execute: <strong>python manage.py runserver</strong></p>
            <p>2. Acesse: <strong>http://localhost:8000</strong></p>
            <p>3. Login: <strong>admin / admin123</strong></p>
            
            <h3>💡 Se ainda não funcionar:</h3>
            <p>• Execute: <strong>python diagnostico.py</strong></p>
            <p>• Verifique firewall/antivírus</p>
            <p>• Reinicie o computador</p>
        </div>
    </div>
</body>
</html>
"""

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

print(f"🌐 Servidor temporário iniciado em http://localhost:{PORT}")
print("⌨️  Pressione Ctrl+C para parar")

try:
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\\n🛑 Servidor parado")
except Exception as e:
    print(f"❌ Erro: {e}")
'''
    
    with open('servidor_temporario.py', 'w', encoding='utf-8') as f:
        f.write(server_code)
    
    print("✅ Servidor temporário criado: servidor_temporario.py")

def start_django_server():
    """Tentar iniciar servidor Django"""
    print("🚀 Tentando iniciar servidor Django...")
    
    # Finalizar processos anteriores
    kill_all_python()
    
    # Encontrar porta livre
    port = find_free_port()
    
    # Tentar diferentes configurações
    commands = [
        [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}'],
        [sys.executable, 'manage.py', 'runserver', f'localhost:{port}'],
        [sys.executable, 'manage.py', 'runserver', f'0.0.0.0:{port}'],
        [sys.executable, 'manage.py', 'runserver', f'{port}']
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"🔄 Tentativa {i}/4: {' '.join(cmd)}")
        
        try:
            # Tentar iniciar servidor
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Aguardar um pouco para o servidor iniciar
            time.sleep(3)
            
            # Verificar se o servidor está rodando
            if test_port(port):
                print(f"❌ Servidor não iniciou na porta {port}")
                process.terminate()
                continue
            else:
                print(f"✅ Servidor Django funcionando na porta {port}!")
                print("=" * 60)
                print("🌐 SERVIDOR INICIADO COM SUCESSO!")
                print(f"📍 Acesse: http://localhost:{port}")
                print(f"📍 Ou tente: http://127.0.0.1:{port}")
                print("🔑 Login: admin / admin123")
                print("⌨️  Pressione Ctrl+C para parar")
                print("=" * 60)
                
                # Aguardar servidor rodar
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Servidor interrompido pelo usuário")
                    process.terminate()
                
                return True
                
        except Exception as e:
            print(f"❌ Erro na tentativa {i}: {e}")
            continue
    
    print("❌ Todas as tentativas falharam!")
    return False

def main():
    """Função principal"""
    print("🔧 FORÇANDO SERVIDOR DJANGO A FUNCIONAR")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ manage.py não encontrado!")
        print("💡 Execute este script na pasta do projeto Django")
        return False
    
    # Tentar iniciar servidor Django
    if start_django_server():
        return True
    
    print("\n⚠️  SERVIDOR DJANGO FALHOU - Iniciando servidor temporário...")
    
    # Criar servidor temporário
    create_minimal_server()
    
    # Tentar executar servidor temporário
    try:
        port = find_free_port()
        print(f"🚀 Iniciando servidor temporário na porta {port}...")
        
        subprocess.run([sys.executable, 'servidor_temporario.py'])
        
    except Exception as e:
        print(f"❌ Erro no servidor temporário: {e}")
    
    print("\n💡 INSTRUÇÕES FINAIS:")
    print("1. Execute: python diagnostico.py")
    print("2. Siga as soluções recomendadas")
    print("3. Reinicie o computador se necessário")
    print("4. Execute: python manage.py runserver")

if __name__ == "__main__":
    main()