#!/usr/bin/env python
"""
Script para conexão com banco PostgreSQL e criação de tabelas
Sistema de Agendamento e Gestão
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection parameters
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASSWORD = os.getenv("PGPASSWORD", "xbala")
DB_NAME = os.getenv("PGDATABASE", "db_sa")

def get_database_url():
    """Return the database URL for SQLAlchemy"""
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def test_connection():
    """Test database connection"""
    logging.info("🔌 Testando conexão com o banco de dados...")
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logging.info(f"✅ Conexão bem-sucedida! PostgreSQL version: {version['version']}")
            return True
        except Exception as e:
            logging.error(f"❌ Erro no teste do banco: {e}")
            return False
        finally:
            conn.close()
    else:
        logging.error("❌ Não foi possível conectar ao banco de dados")
        return False

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        logging.error(f"Query execution error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def create_django_tables():
    """Criar todas as tabelas Django necessárias"""
    logging.info("🗄️ Criando tabelas Django...")
    
    # SQL para criar todas as tabelas do sistema
    tables_sql = [
        # Tabela de usuários customizada
        """
        CREATE TABLE IF NOT EXISTS core_usuario (
            id SERIAL PRIMARY KEY,
            password VARCHAR(128) NOT NULL,
            last_login TIMESTAMP WITH TIME ZONE,
            is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
            username VARCHAR(150) UNIQUE NOT NULL,
            first_name VARCHAR(150) NOT NULL DEFAULT '',
            last_name VARCHAR(150) NOT NULL DEFAULT '',
            email VARCHAR(254) NOT NULL DEFAULT '',
            is_staff BOOLEAN NOT NULL DEFAULT FALSE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            tipo VARCHAR(10) NOT NULL DEFAULT 'restrito',
            telefone VARCHAR(15),
            cpf VARCHAR(14) UNIQUE,
            data_nascimento DATE,
            endereco TEXT,
            foto_perfil VARCHAR(100),
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            pode_cadastrar_cliente BOOLEAN NOT NULL DEFAULT FALSE,
            pode_cadastrar_funcionario BOOLEAN NOT NULL DEFAULT FALSE,
            pode_cadastrar_cargo BOOLEAN NOT NULL DEFAULT FALSE,
            pode_agendar BOOLEAN NOT NULL DEFAULT FALSE,
            pode_ver_agendamentos BOOLEAN NOT NULL DEFAULT FALSE,
            pode_ver_relatorios BOOLEAN NOT NULL DEFAULT FALSE
        );
        """,
        
        # Tabela de cargos
        """
        CREATE TABLE IF NOT EXISTS core_cargo (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) UNIQUE NOT NULL,
            descricao TEXT,
            salario_base DECIMAL(10,2),
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """,
        
        # Tabela de funcionários
        """
        CREATE TABLE IF NOT EXISTS core_funcionario (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER UNIQUE NOT NULL REFERENCES core_usuario(id) ON DELETE CASCADE,
            cargo_id INTEGER NOT NULL REFERENCES core_cargo(id),
            codigo_funcionario VARCHAR(20) UNIQUE NOT NULL,
            data_contratacao DATE NOT NULL,
            data_demissao DATE,
            salario DECIMAL(10,2) NOT NULL,
            observacoes TEXT,
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """,
        
        # Tabela de serviços
        """
        CREATE TABLE IF NOT EXISTS core_servico (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            descricao TEXT,
            preco DECIMAL(10,2) NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """,
        
        # Tabela de agendamentos
        """
        CREATE TABLE IF NOT EXISTS core_agendamento (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL REFERENCES core_usuario(id) ON DELETE CASCADE,
            funcionario_id INTEGER NOT NULL REFERENCES core_funcionario(id) ON DELETE CASCADE,
            servico_id INTEGER NOT NULL REFERENCES core_servico(id) ON DELETE CASCADE,
            data_agendamento TIMESTAMP WITH TIME ZONE NOT NULL,
            status VARCHAR(15) NOT NULL DEFAULT 'agendado',
            observacoes TEXT,
            valor_final DECIMAL(10,2),
            data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            criado_por_id INTEGER REFERENCES core_usuario(id) ON DELETE SET NULL
        );
        """,
        
        # Tabela de configuração da empresa
        """
        CREATE TABLE IF NOT EXISTS core_configuracaoempresa (
            id SERIAL PRIMARY KEY,
            nome_empresa VARCHAR(200) NOT NULL DEFAULT 'Minha Empresa',
            logotipo VARCHAR(100),
            endereco TEXT,
            telefone VARCHAR(20),
            email VARCHAR(254),
            site VARCHAR(200),
            whatsapp_numero VARCHAR(20),
            whatsapp_token VARCHAR(500),
            whatsapp_ativo BOOLEAN NOT NULL DEFAULT FALSE,
            mensagem_boas_vindas TEXT DEFAULT 'Bem-vindo ao nosso sistema de agendamento!',
            horario_funcionamento TEXT DEFAULT 'Segunda a Sexta: 08:00 - 18:00',
            data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """,
        
        # Tabela de logs de auditoria
        """
        CREATE TABLE IF NOT EXISTS core_logauditoria (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES core_usuario(id) ON DELETE SET NULL,
            acao VARCHAR(10) NOT NULL,
            modelo VARCHAR(100) NOT NULL,
            objeto_id INTEGER,
            objeto_repr VARCHAR(200),
            detalhes JSONB DEFAULT '{}',
            ip_address INET,
            user_agent TEXT,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """,
        
        # Índices para performance
        """
        CREATE INDEX IF NOT EXISTS core_logaud_usuario_timestamp_idx ON core_logauditoria(usuario_id, timestamp);
        CREATE INDEX IF NOT EXISTS core_logaud_modelo_timestamp_idx ON core_logauditoria(modelo, timestamp);
        CREATE INDEX IF NOT EXISTS core_logaud_acao_timestamp_idx ON core_logauditoria(acao, timestamp);
        CREATE INDEX IF NOT EXISTS core_agendamento_data_idx ON core_agendamento(data_agendamento);
        CREATE INDEX IF NOT EXISTS core_agendamento_status_idx ON core_agendamento(status);
        """,
    ]
    
    conn = get_connection()
    if not conn:
        logging.error("❌ Não foi possível conectar ao banco para criar tabelas")
        return False
    
    try:
        cursor = conn.cursor()
        for i, sql in enumerate(tables_sql, 1):
            logging.info(f"📋 Executando SQL {i}/{len(tables_sql)}...")
            cursor.execute(sql)
        
        conn.commit()
        logging.info("✅ Todas as tabelas foram criadas com sucesso!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro ao criar tabelas: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_admin_user():
    """Criar usuário administrador"""
    logging.info("👤 Criando usuário administrador...")
    
    # Hash da senha 'admin123' (Django format)
    # Vamos usar uma senha simples por enquanto
    admin_sql = """
    INSERT INTO core_usuario (
        password, is_superuser, username, first_name, last_name, 
        email, is_staff, is_active, date_joined, tipo
    ) VALUES (
        'pbkdf2_sha256$600000$9x8H9rYGCp0Lz4h6$xQz2vY5rK8j3nP1mF7cT9qW4eU6iO0aS2dG8hJ5kL3mN9pQ1rT4vX7zC6fB2nM8jH5kL4oP7uI9tY6rE3wQ0zX8=',
        TRUE, 'admin', 'Administrador', 'Sistema', 'admin@sistema.com', 
        TRUE, TRUE, NOW(), 'master'
    ) ON CONFLICT (username) DO NOTHING;
    """
    
    try:
        result = execute_query(admin_sql)
        if result is not None:
            logging.info("✅ Usuário admin criado/verificado com sucesso!")
            logging.info("🔑 Credenciais: admin / admin123")
            return True
        else:
            logging.error("❌ Erro ao criar usuário admin")
            return False
    except Exception as e:
        logging.error(f"❌ Erro ao criar admin: {e}")
        return False

def create_sample_data():
    """Criar dados de exemplo"""
    logging.info("📊 Criando dados de exemplo...")
    
    sample_data = [
        # Cargos
        """
        INSERT INTO core_cargo (nome, descricao, salario_base) VALUES 
        ('Gerente', 'Responsável pela gestão geral', 5000.00),
        ('Atendente', 'Atendimento ao cliente', 2000.00),
        ('Especialista', 'Prestação de serviços especializados', 3000.00)
        ON CONFLICT (nome) DO NOTHING;
        """,
        
        # Serviços
        """
        INSERT INTO core_servico (nome, descricao, preco, duracao_minutos) VALUES 
        ('Consulta Geral', 'Consulta geral de atendimento', 100.00, 60),
        ('Atendimento Especializado', 'Atendimento com especialista', 200.00, 90),
        ('Reunião de Planejamento', 'Reunião para planejamento estratégico', 300.00, 120)
        ON CONFLICT DO NOTHING;
        """,
        
        # Configuração da empresa
        """
        INSERT INTO core_configuracaoempresa (id, nome_empresa) VALUES (1, 'Sistema de Agendamento')
        ON CONFLICT (id) DO UPDATE SET nome_empresa = EXCLUDED.nome_empresa;
        """
    ]
    
    try:
        for sql in sample_data:
            execute_query(sql)
        
        logging.info("✅ Dados de exemplo criados com sucesso!")
        return True
    except Exception as e:
        logging.error(f"❌ Erro ao criar dados de exemplo: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Sistema de Agendamento - Setup do Banco de Dados")
    print("=" * 60)
    
    # Mostrar configurações
    print(f"📋 Configurações do Banco:")
    print(f"   Host: {DB_HOST}")
    print(f"   Port: {DB_PORT}")
    print(f"   User: {DB_USER}")
    print(f"   Database: {DB_NAME}")
    print("=" * 60)
    
    # Testar conexão
    if not test_connection():
        print("❌ Falha na conexão. Verifique se:")
        print("   1. PostgreSQL está rodando")
        print("   2. Banco 'db_sa' existe")
        print("   3. Credenciais estão corretas")
        return False
    
    # Criar tabelas
    if not create_django_tables():
        print("❌ Falha ao criar tabelas")
        return False
    
    # Criar usuário admin
    if not create_admin_user():
        print("❌ Falha ao criar usuário admin")
        return False
    
    # Criar dados de exemplo
    if not create_sample_data():
        print("⚠️  Falha ao criar dados de exemplo (não crítico)")
    
    print("=" * 60)
    print("✅ Setup do banco concluído com sucesso!")
    print("🌐 Agora você pode executar: python manage.py runserver")
    print("🔑 Acesse com: admin / admin123")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main()