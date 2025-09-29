-- Migração inicial: tabelas básicas para tenancy e auditoria

-- Tabela de tenants (isolamento multi-tenant)
CREATE TABLE tenant (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de companies (empresas dentro de um tenant)
CREATE TABLE company (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE,  -- código único da empresa
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de log de auditoria (para compliance e debugging)
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id) ON DELETE SET NULL,
    user_id VARCHAR(255),  -- pode ser ID do usuário ou sistema
    action VARCHAR(255) NOT NULL,  -- ex: 'create_incident', 'query_metrics'
    resource_type VARCHAR(100),  -- ex: 'incident', 'asset'
    resource_id VARCHAR(255),  -- ID do recurso afetado
    details JSONB,  -- dados adicionais em JSON
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_company_tenant_id ON company(tenant_id);
CREATE INDEX idx_audit_log_tenant_id ON audit_log(tenant_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_action ON audit_log(action);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tenant_updated_at BEFORE UPDATE ON tenant FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_company_updated_at BEFORE UPDATE ON company FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();