# Especificação funcional e técnica — “Agente Super Tools”

## 1. Objetivo
Entregar uma plataforma multi-tenant que expõe “agentes” de Suporte e Cliente para consultar e executar ações em Observabilidade e ITSM. Acesso via chat, web ou app. Isolamento por tenant e company. Autorização central via Keycloak. Integração a sistemas legados via adapters. O LLM nunca acessa APIs finais direto. Usa MCP Broker como orquestrador de ferramentas.

## 2. Escopo
- Autenticação e autorização com Keycloak.
- Tenancy por linha de dados no Postgres com RLS.
- MCP Broker com ferramentas padronizadas.
- Adapters para Observability e ITSM.
- Channel Gateway de entrada unificada.
- Cache e rate limit com Redis.
- Auditoria e métricas.
- Deploy com Docker Compose ou Kubernetes.

Fora de escopo por agora: UI própria rica. Integrações além de Observability e ITSM.

## 3. Arquitetura lógica
- Channel Gateway → valida JWT Keycloak e normaliza o canal.
- Agents Layer → decide intenção e chama o MCP Broker.
- MCP Broker → aplica escopo, chama ferramentas, registra auditoria.
- Adapters Layer → encapsula APIs de Observability e ITSM.
- Postgres → dados de tenancy, mapeamentos, auditoria.
- Redis → cache, locks, rate limit.

## 4. Autenticação e Autorização
- Keycloak
  - Realm: `supertools`.
  - Clients: `channel-gateway` (public), `agents` (confidential), `mcp-broker` (confidential), `adapter-observ` e `adapter-itsm` (confidential).
  - Roles de alto nível: `support_agent`, `end_customer`, `admin_tenant`.
  - Claims no token:
    - `tenant_id` string.
    - `company_ids` array.
    - `scopes` array. Exemplos: `observ.read`, `observ.action`, `itsm.read`, `itsm.incident.write`.
- AutZ
  - No Broker: checa scopes e interseção de company_ids.
  - No Postgres: RLS por `tenant_id` e `company_id`.

## 5. Modelo de dados Postgres
Tabelas base. Criar migrações.

```sql
create type tool_type as enum ('observability','itsm');

create table tenant (
  id uuid primary key,
  name text not null,
  status text not null default 'active'
);

create table company (
  id uuid primary key,
  tenant_id uuid not null references tenant(id),
  name text not null,
  unique(tenant_id, name)
);

create table user_company_scope (
  sub text not null,
  tenant_id uuid not null references tenant(id),
  company_id uuid not null references company(id),
  scopes text[] not null,
  primary key(sub, company_id)
);

create table adapter_endpoint (
  id uuid primary key,
  tenant_id uuid not null references tenant(id),
  kind tool_type not null,
  base_url text not null,
  client_id text not null,
  client_secret text not null,
  extra jsonb not null default '{}'
);

create table audit_log (
  id bigserial primary key,
  ts timestamptz not null default now(),
  sub text not null,
  tenant_id uuid not null,
  company_id uuid,
  tool text not null,
  action text not null,
  args jsonb,
  result_code int,
  latency_ms int
);
```

RLS:

```sql
alter table user_company_scope enable row level security;
alter table audit_log enable row level security;

create policy scope_read on user_company_scope
using (tenant_id::text = current_setting('app.tenant_id', true));

create policy audit_tenant on audit_log
using (tenant_id::text = current_setting('app.tenant_id', true));
```

No Broker, antes de query, set:

```sql
select set_config('app.tenant_id', :tenant_id, true);
```

## 6. Redis
- Chaves
  - `rl:<sub>` contador sliding window por minuto.
  - `cache:observ:<tenant>:<company>:<key>` TTL curto 60 s.
  - `lock:<tenant>:<company>:<resource>` TTL 30 s.
- Implementar rate limit padrão 60 req/min por sub. Parametrizável por tenant.

## 7. Contratos MCP Broker
Expor o Broker como servidor MCP. Ferramentas mínimas.

### 7.1 Tool `observ.search_assets`
Entrada:
```json
{"query":"switch core site X","company_ids":["..."],"limit":50}
```
Saída:
```json
{"items":[{"id":"node-123","name":"SW-Core-01","type":"node","site":"DC-A"}]}
```

### 7.2 Tool `observ.get_metrics`
Entrada:
```json
{"asset_id":"node-123","metric":"cpu_util","range":"1h","company_id":"..."}
```
Saída:
```json
{"series":[["2025-09-28T18:00Z",12.3],["2025-09-28T18:05Z",15.1]]}
```

### 7.3 Tool `itsm.create_incident`
Entrada:
```json
{"company_id":"...","short_description":"Link down","description":"...","ci":"SW-Core-01","impact":"3","urgency":"3"}
```
Saída:
```json
{"incident_id":"INC00012345","url":"https://itsm/INC00012345"}
```

### 7.4 Tool `itsm.update_incident`
Entrada:
```json
{"incident_id":"INC00012345","company_id":"...","note":"Auto enrichment attached","status":"In Progress"}
```
Saída:
```json
{"ok":true}
```

Validações no Broker:
- `tenant_id` do token é obrigatório.
- `company_id` de cada chamada deve existir em `user_company_scope`.
- Scopes por ferramenta.

Auditoria em todas as ferramentas.

## 8. Contratos dos Adapters

### 8.1 Adapter Observability
REST privado. JWT de serviço emitido pelo Keycloak. Headers:
- `X-Tenant-Id`, `X-Company-Id`, `X-Sub`, `X-Scopes`.

Endpoints:

```
GET /assets/search?q=...&limit=...
GET /metrics/{asset_id}?metric=...&range=...
POST /actions/poll-now { "asset_id": "..." }
```

### 8.2 Adapter ITSM
Endpoints:

```
POST /incidents
PATCH /incidents/{id}
GET /incidents/{id}
```

### 8.3 Regras comuns
- Timeouts 10 s por hop.
- Retries com backoff para 5xx e timeouts.
- Circuit breaker por host.
- Logs estruturados. Correlation ID `X-Req-Id`.

## 9. Channel Gateway
Funções:
- Recebe mensagens dos canais.
- Valida JWT do Keycloak.
- Envia intent + payload para Agents via HTTP interno.
- Propaga `X-Req-Id`, `Authorization`.

Contrato de saída para Agents:
```json
{"sub":"...","tenant_id":"...","company_ids":["..."],"text":"cpu do core","channel":"web"}
```

## 10. Agents Layer
- Detecta intenção simples via regras ou LLM local.
- Chama MCP Broker pela ferramenta adequada.
- Formata a resposta para o canal.

Pseudocódigo:

```python
def handle(msg):
    intent = classify(msg.text)
    if intent == "metric":
        return mcp.call("observ.get_metrics", {...})
    if intent == "incident_open":
        return mcp.call("itsm.create_incident", {...})
```

## 11. Segurança
- Segredos cifrados AES-GCM. Chave via MASTER_KEY.
- Tokens de serviço com audience por adapter.
- TLS obrigatório.
- RLS ativa.

## 12. Observabilidade
- Prometheus metrics.
- Logs JSON com req_id e tenant.
- Tracing OpenTelemetry.

## 13. Variáveis de ambiente
```
KEYCLOAK_URL=
KEYCLOAK_REALM=supertools
KEYCLOAK_CLIENT_ID_MCP=
KEYCLOAK_CLIENT_SECRET_MCP=
DB_URL=postgresql+psycopg://user:pass@host:5432/supertools
REDIS_URL=redis://host:6379/0
MASTER_KEY_BASE64=
RATE_LIMIT_PER_MINUTE=60
HTTP_TIMEOUT_SECONDS=10
```

## 14. Estrutura de repositórios
- channel-gateway/
- agents/
- mcp-broker/
- adapters/observability/
- adapters/itsm/
- infra/
- db/
- docs/

## 15. Docker Compose base
```yaml
version: "3.9"
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: postgres
    ports: ["5432:5432"]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
    command: start --hostname-strict=false
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
    ports: ["8080:8080"]
  mcp-broker:
    build: ./mcp-broker
    environment: [DB_URL, REDIS_URL, KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID_MCP, KEYCLOAK_CLIENT_SECRET_MCP, MASTER_KEY_BASE64]
    depends_on: [postgres, redis, keycloak]
    ports: ["9000:9000"]
  adapter-observ:
    build: ./adapters/observability
    environment: [KEYCLOAK_URL, KEYCLOAK_REALM]
    depends_on: [mcp-broker]
    ports: ["9010:9010"]
  adapter-itsm:
    build: ./adapters/itsm
    environment: [KEYCLOAK_URL, KEYCLOAK_REALM]
    ports: ["9020:9020"]
  agents:
    build: ./agents
    environment: [KEYCLOAK_URL, KEYCLOAK_REALM]
    depends_on: [mcp-broker]
    ports: ["9100:9100"]
  channel-gateway:
    build: ./channel-gateway
    depends_on: [agents]
    ports: ["9200:9200"]
```

## 16. Endpoints do Broker para Adapters
```
GET /health
POST /mcp/<tool_name>
```

## 17. Erros e códigos
- 400 input inválido.
- 401 token inválido.
- 403 escopo insuf.
- 404 recurso não encontrado.
- 409 conflito.
- 429 rate limit.
- 5xx backend.

## 18. Testes
- Unitários e integração.
- RLS validações.
- Rate limit.
- Auditoria.

## 19. Critérios de aceite
- Usuário restrito a company_ids.
- Métricas < 2s local.
- Incidente criado com URL.
- Auditoria 100%.
- Rate limit ativo.

## 20. Roadmap curto
1. DB, RLS, migrações e audit.
2. Broker stub.
3. Adapter Observability.
4. Adapter ITSM.
5. Agents e Gateway mínimos.
6. Telemetria e rate limit.
7. Hardening e testes.
