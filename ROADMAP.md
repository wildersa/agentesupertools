# Roadmap - Agente Super Tools

## 📋 Visão Geral do Projeto

**Objetivo**: Plataforma multi-tenant de agentes para Suporte/Cliente que consulta e executa ações em ferramentas de Observabilidade e ITSM via chat/web/app, com isolamento por tenant→company e autorização centralizada.

---

## 🎯 MVPs (Minimum Viable Products)

### MVP 1: Chat Básico com Gateway de Observability

**Prazo**: 3-4 semanas  
**Objetivo**: Demonstrar chat respondendo e interagindo com ferramentas de gateway básicas

**Funcionalidades**:

- ✅ Channel Gateway básico (API REST)
- ✅ Agente simples que responde via MCP
- ✅ Adapter de Observability mockado/básico
- ✅ Consulta de assets e métricas básicas
- ✅ Autenticação simples (sem Keycloak ainda)

**Demonstração**:

- Usuário pergunta "CPU do servidor X"
- Sistema retorna métricas básicas via chat

### MVP 2: Gestão de Incidentes via ITSM

**Prazo**: 4-5 semanas após MVP1  
**Objetivo**: Agente interagindo com incidentes via gateway de ITSM

**Funcionalidades**:

- ✅ Adapter ITSM funcional
- ✅ Criação, consulta e atualização de incidentes
- ✅ Enriquecimento básico de tickets
- ✅ Integração com dados de observability

**Demonstração**:

- "Abrir incidente para servidor X com problema Y"
- "Status do incidente INC123456"
- "Atualizar incidente com dados de monitoramento"

---

## 🗺️ Roadmap Completo por Fases

## Fase 0: Preparação e Setup Inicial

**Duração**: 1 semana

### Milestone 0.1: Infraestrutura Base

- [ ] Setup do repositório com estrutura de pastas
- [ ] Configuração inicial do Docker Compose
- [ ] Setup Postgres com migrações básicas
- [ ] Setup Redis básico
- [ ] Documentação inicial de desenvolvimento

**Critérios de Aceite**:

- [ ] `docker-compose up` funciona
- [ ] Postgres conecta e aceita migrações
- [ ] Redis está acessível
- [ ] Estrutura de pastas criada conforme especificação

---

## Fase 1: MVP1 - Chat Básico com Observability

**Duração**: 3-4 semanas

### Milestone 1.1: MCP Broker Básico

**Prazo**: 1 semana

- [ ] Implementar MCP Broker stub
- [ ] Estrutura básica de ferramentas MCP
- [ ] Tool `observ.search_assets` básica
- [ ] Tool `observ.get_metrics` básica
- [ ] Validação de entrada das tools
- [ ] Logs estruturados básicos

**Critérios de Aceite**:

- [ ] MCP Broker responde na porta 9000
- [ ] Tools retornam dados mockados válidos
- [ ] Logs aparecem em formato JSON
- [ ] Health check funciona

### Milestone 1.2: Adapter Observability Mockado

**Prazo**: 1 semana

- [ ] API REST básica do adapter
- [ ] Endpoints `/assets/search` e `/metrics/{id}`
- [ ] Dados mockados realistas
- [ ] Timeouts e error handling básicos
- [ ] Headers de correlação

**Critérios de Aceite**:

- [ ] Adapter responde na porta 9010
- [ ] Retorna dados em formato esperado pelo Broker
- [ ] Simula latência realista (100-300ms)
- [ ] Error handling para casos inválidos

### Milestone 1.3: Channel Gateway Básico

**Prazo**: 1 semana

- [ ] API REST para receber mensagens
- [ ] Parsing básico de intents
- [ ] Roteamento para Agents
- [ ] Autenticação stub (bearer token simples)
- [ ] CORS habilitado

**Critérios de Aceite**:

- [ ] Gateway responde na porta 9200
- [ ] Aceita POST com mensagens
- [ ] Roteia para agents corretamente
- [ ] Retorna respostas formatadas

### Milestone 1.4: Agents Layer Simples

**Prazo**: 1 semana

- [ ] Agent básico que classifica intents
- [ ] Chamadas para MCP Broker
- [ ] Formatação de respostas para chat
- [ ] Tratamento de erros básico

**Critérios de Aceite**:

- [ ] Agent identifica intent "metric" e "asset_search"
- [ ] Chama MCP tools apropriadas
- [ ] Retorna resposta legível para humano
- [ ] Funciona end-to-end: Gateway → Agent → MCP → Adapter

**🎯 Entrega MVP1**: Chat básico funcionando com consultas de observability

---

## Fase 2: MVP2 - Gestão de Incidentes ITSM

**Duração**: 4-5 semanas

### Milestone 2.1: Adapter ITSM

**Prazo**: 2 semanas

- [ ] API REST do adapter ITSM
- [ ] Endpoints para CRUD de incidentes
- [ ] Integração com ITSM real ou mock avançado
- [ ] Validação de dados de entrada
- [ ] Mapeamento de campos padronizados

**Critérios de Aceite**:

- [ ] POST `/incidents` cria incidente
- [ ] PATCH `/incidents/{id}` atualiza
- [ ] GET `/incidents/{id}` consulta
- [ ] Retorna IDs e URLs válidas
- [ ] Error handling robusto

### Milestone 2.2: Tools MCP para ITSM

**Prazo**: 1 semana

- [ ] Tool `itsm.create_incident`
- [ ] Tool `itsm.update_incident`
- [ ] Tool `itsm.get_incident`
- [ ] Validação de campos obrigatórios
- [ ] Integração com adapter ITSM

**Critérios de Aceite**:

- [ ] Tools funcionam via MCP Broker
- [ ] Validam company_id e campos
- [ ] Retornam dados estruturados
- [ ] Logs de auditoria básicos

### Milestone 2.3: Agente de Incidentes

**Prazo**: 1-2 semanas

- [ ] Intent classification para incidentes
- [ ] "Abrir incidente" com parsing de parâmetros
- [ ] "Consultar incidente" por número
- [ ] "Atualizar incidente" com novas informações
- [ ] Enriquecimento com dados de observability

**Critérios de Aceite**:

- [ ] "Abrir incidente para servidor X" funciona
- [ ] "Status do INC123456" retorna detalhes
- [ ] "Atualizar INC123456 com CPU alta" adiciona dados
- [ ] Integração observability + ITSM funciona

**🎯 Entrega MVP2**: Gestão completa de incidentes via chat

---

## Fase 3: Autenticação e Segurança

**Duração**: 3-4 semanas

### Milestone 3.1: Keycloak Setup

**Prazo**: 1 semana

- [ ] Configuração Keycloak no compose
- [ ] Realm `supertools` criado
- [ ] Clients configurados
- [ ] Roles e claims básicos
- [ ] Documentação de setup

### Milestone 3.2: Autenticação JWT

**Prazo**: 2 semanas

- [ ] Validação JWT no Channel Gateway
- [ ] Extração de `tenant_id` e `company_ids`
- [ ] Propagação de headers de autenticação
- [ ] Middleware de autenticação nos adapters
- [ ] Tratamento de tokens expirados

### Milestone 3.3: Autorização Básica

**Prazo**: 1-2 semanas

- [ ] Validação de scopes nas tools MCP
- [ ] Filtro por company_id nas consultas
- [ ] RBAC básico para diferentes tipos de usuário
- [ ] Logs de tentativas não autorizadas

**Critérios de Aceite**:

- [ ] Usuário sem token é rejeitado
- [ ] Usuário vê apenas dados da sua company
- [ ] Scopes controlam acesso às tools
- [ ] Auditoria registra tentativas inválidas

---

## Fase 4: Modelo de Dados e Tenancy

**Duração**: 2-3 semanas

### Milestone 4.1: Schema Postgres Completo

**Prazo**: 1 semana

- [ ] Tabelas tenant, company, user_company_scope
- [ ] Tabela adapter_endpoint
- [ ] Tabela audit_log
- [ ] Índices otimizados
- [ ] Migrações versionadas

### Milestone 4.2: Row Level Security (RLS)

**Prazo**: 1-2 semanas

- [ ] RLS habilitado nas tabelas
- [ ] Políticas por tenant_id
- [ ] Configuração de contexto nas queries
- [ ] Testes de isolamento
- [ ] Documentação de segurança

**Critérios de Aceite**:

- [ ] Usuário A não vê dados do tenant B
- [ ] Queries automáticas filtram por tenant
- [ ] Tentativas de bypass são logadas
- [ ] Performance mantida com RLS

---

## Fase 5: Cache e Performance

**Duração**: 2-3 semanas

### Milestone 5.1: Redis Cache

**Prazo**: 1-2 semanas

- [ ] Cache de consultas frequentes
- [ ] TTL configurável por tipo de dados
- [ ] Invalidação inteligente
- [ ] Métricas de hit/miss ratio
- [ ] Fallback para fonte original

### Milestone 5.2: Rate Limiting

**Prazo**: 1 semana

- [ ] Rate limit por usuário/tenant
- [ ] Sliding window no Redis
- [ ] Diferentes limites por tipo de operação
- [ ] Headers informativos de limite
- [ ] Configuração via environment

**Critérios de Aceite**:

- [ ] Consultas frequentes são cached
- [ ] Rate limit funciona por tenant
- [ ] Performance melhorada significativamente
- [ ] Métricas de cache disponíveis

---

## Fase 6: Observabilidade e Monitoramento

**Duração**: 2 semanas

### Milestone 6.1: Métricas e Logs

**Prazo**: 1 semana

- [ ] Prometheus metrics
- [ ] Logs estruturados JSON
- [ ] Tracing básico com correlation ID
- [ ] Health checks detalhados
- [ ] Dashboard Grafana básico

### Milestone 6.2: Auditoria Completa

**Prazo**: 1 semana

- [ ] Log de todas as operações
- [ ] Retenção configurável
- [ ] Relatórios de uso por tenant
- [ ] Alertas para ações suspeitas
- [ ] Exportação para compliance

**Critérios de Aceite**:

- [ ] Todas as chamadas são auditadas
- [ ] Métricas mostram performance real
- [ ] Alerts funcionam para problemas
- [ ] Dashboard mostra status geral

---

## Fase 7: Hardening e Produção

**Duração**: 2-3 semanas

### Milestone 7.1: Segurança Avançada

**Prazo**: 1-2 semanas

- [ ] Criptografia de segredos
- [ ] TLS em todas as comunicações
- [ ] Sanitização de inputs
- [ ] Proteção contra ataques comuns
- [ ] Auditoria de segurança

### Milestone 7.2: Testes e Qualidade

**Prazo**: 1 semana

- [ ] Testes unitários (>80% coverage)
- [ ] Testes de integração
- [ ] Testes de carga básicos
- [ ] Testes de segurança
- [ ] CI/CD pipeline

### Milestone 7.3: Deploy e Documentação

**Prazo**: 1 semana

- [ ] Configuração Kubernetes
- [ ] Scripts de deploy automatizado
- [ ] Documentação de operação
- [ ] Runbooks para problemas comuns
- [ ] Guia de troubleshooting

**Critérios de Aceite**:

- [ ] Sistema passa em testes de segurança
- [ ] Deploy automatizado funciona
- [ ] Documentação completa e atualizada
- [ ] Pronto para produção

---

## 📊 Cronograma Resumido

| Fase | Duração | Marco Principal |
|------|---------|----------------|
| 0 | 1 semana | Infraestrutura base |
| 1 | 3-4 semanas | **MVP1: Chat + Observability** |
| 2 | 4-5 semanas | **MVP2: Gestão de Incidentes** |
| 3 | 3-4 semanas | Autenticação completa |
| 4 | 2-3 semanas | Tenancy e RLS |
| 5 | 2-3 semanas | Cache e performance |
| 6 | 2 semanas | Observabilidade |
| 7 | 2-3 semanas | Produção |

**Total Estimado**: 19-25 semanas (~5-6 meses)

---

## 🎯 Marcos de Demonstração

### Demo 1 (Semana 4): MVP1 Funcionando

- Chat simples respondendo consultas de observability
- "Mostrar CPU do servidor web-01"
- "Listar servidores do site DC-A"

### Demo 2 (Semana 9): MVP2 Completo

- Gestão completa de incidentes via chat
- "Abrir incidente para servidor com problema"
- "Atualizar incidente com dados de monitoramento"

### Demo 3 (Semana 13): Versão Segura

- Múltiplos tenants isolados
- Autenticação e autorização funcionando
- Dashboard de métricas

### Demo 4 (Semana 19): Versão Produção

- Sistema completo e otimizado
- Cache, rate limiting, auditoria
- Pronto para carga real

---

## 🔧 Stack Tecnológico

**Backend**: Python 3.11+, FastAPI, SQLAlchemy  
**MCP**: fastmcp library  
**Database**: PostgreSQL 16 com Row Level Security  
**Cache**: Redis 7  
**Auth**: Keycloak  
**Containerization**: Docker + Docker Compose  
**Orchestration**: Kubernetes (opcional)  
**Monitoring**: Prometheus + Grafana  
**Logging**: Structured JSON logs  

---

## 📋 Checklist de Entrega Final

### Funcionalidades Core

- [ ] Chat multi-canal funcionando
- [ ] Agentes Suporte e Cliente operacionais  
- [ ] Integração completa Observability + ITSM
- [ ] Autenticação e autorização robustas
- [ ] Isolamento completo por tenant

### Qualidade e Segurança

- [ ] Testes automatizados (>80% coverage)
- [ ] Segurança validada e auditada
- [ ] Performance otimizada com cache
- [ ] Monitoramento e alertas ativos
- [ ] Documentação completa

### Deploy e Operação

- [ ] Deploy automatizado funcional
- [ ] Backup e recovery testados
- [ ] Runbooks de operação criados
- [ ] Treinamento da equipe realizado
- [ ] Go-live planejado e executado

---

## 🚀 Próximos Passos Imediatos

### Semana 1: Setup e Preparação

1. **Dia 1-2**: Estrutura do repositório
   - Criar estrutura de pastas conforme especificação
   - Setup inicial do pyproject.toml e dependencies
   - Configurar Docker Compose básico

2. **Dia 3-4**: Banco de dados
   - Setup PostgreSQL com migrações
   - Criar tabelas básicas (tenant, company, audit_log)
   - Testar conexões

3. **Dia 5**: Redis e documentação
   - Setup Redis
   - Documentar ambiente de desenvolvimento
   - Testar toda a stack básica

### Semana 2-4: MVP1 Development

**Foco**: Entregar chat básico que consulta observability

**Ordem de desenvolvimento sugerida**:

1. MCP Broker com tools mockadas
2. Adapter Observability com dados fake
3. Agent básico para classificar intents
4. Channel Gateway para receber mensagens
5. Integração end-to-end

---

*Este roadmap será atualizado conforme o progresso do projeto e feedback das demonstrações.*