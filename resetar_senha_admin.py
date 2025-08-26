#!/usr/bin/env python
"""
Script simples para resetar senha do admin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento_sistema.settings')
django.setup()

from core.models import Usuario

def resetar_senha_admin():
    """Resetar senha do usuário admin"""
    print("🔐 RESETANDO SENHA DO ADMIN")
    print("=" * 40)
    
    try:
        # Procurar usuário admin
        admin = Usuario.objects.get(username='admin')
        
        # Resetar senha
        admin.set_password('admin123')
        admin.is_active = True
        admin.ativo = True
        admin.save()
        
        print("✅ Senha resetada com sucesso!")
        print()
        print("🔑 CREDENCIAIS ATUALIZADAS:")
        print("   Username: admin")
        print("   Password: admin123")
        print()
        print("🌐 Acesse: http://localhost:8000")
        
    except Usuario.DoesNotExist:
        print("❌ Usuário admin não encontrado!")
        print("💡 Execute: python corrigir_login.py")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    resetar_senha_admin()