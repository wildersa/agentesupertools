# Architecture Definition Document (ADD)

## 0. Contexto e objetivo
Guia de arquitetura para expor Observability (SolarWinds) e ITSM (Remedy→ServiceNow) via um **MCP** multi‑tenant, com segurança, limitação por tenant/company e governança de dados.

---
## 1. Visão de negócio
- **Drivers**: automação de NOC, redução de MTTR, padronização de integrações, segurança multi‑tenant.
- **KPIs**: TTR, % tickets auto‑abertos, erros por autorização, SLA chamadas MCP, custo/tenant.
- **Escopo**: tenants clientes, empresas/grupos (company), nodes, incident/work info.
- **Fora de escopo**: UI final, gestão de contratos, billing.

### 1.1 Camada de Acesso e Agentes (novo)
- **Channel Gateway (chat)**: web/app/whatsapp/slack. Gerencia sessões, autentica via Keycloak, injeta `tenant_id`.
- **Dois agentes**:
  - **Agente de Suporte (analista)**: acesso amplo às tools internas e MCP externo, sob RBAC forte. Uso interno apenas.
  - **Chatbot do Cliente**: funções limitadas e pré‑aprovadas. Escopo reduzido, só leitura de dados do próprio tenant/company e ações definidas.
- **Policy por agente**: cada agente tem *allowlist* de tools, limites de ação, quotas e prompts templated.
- **Auditoria por sessão**: logs por `session_id`, `user_sub`, `agent`, `tools usadas`.

## 2. Decisões de arquitetura (resumo)
- **Identidade única**: Keycloak. JWT com `tenant_id`, roles e escopo de companies.
- **Broker**: MCP fino. RBAC+ABAC na borda. Tools = gateways existentes.
- **Arquitetura agnóstica**: **Ports & Adapters (Hexagonal)**. Conectores para **Observability** e **ITSM** substituíveis sem impacto nas tools do MCP.
- **Backends**: contas técnicas por tenant em qualquer ITSM/Observability compatível.
- **Chave canônica**: `company_sys_id` do ITSM. Mesmo valor em SolarWinds (CP) ou equivalente no provedor atual.
- **Mapa**: Postgres para `tenant_id ↔ company_sys_id` (+ cache Redis).
- **Guardrails**: pré‑filtro por tenant/company em toda query; proveniência; auditoria.

### 2.1 Princípio de agnosticidade
- APIs do MCP **não expõem marcas** (ex.: "ServiceNow", "SolarWinds").
- Cada domínio tem **contratos neutros**: Incident, WorkInfo, Node, Alert, CP.
- Conectores implementam **adapters** específicos por fornecedor.
- Troca de fornecedor = **troca de adapter**, contratos MCP permanecem.

## 3. Requisitos
### 3.1 Funcionais
- F1: Autenticar usuário via Keycloak e emitir token com `tenant_id`.
- F2: Expor tools MCP: `get_nodes`, `get_alerts`, `get_incident`, `update_incident`, `get_workinfo`, `create_incident`, `create_workinfo`.
- F3: Aplicar filtros obrigatórios por `tenant_id` e `company_sys_id` em toda chamada.
- F4: ETL de companies do ITSM → Postgres → CP no SolarWinds.
- F5: Auditoria de todas as chamadas com correlação.
- **F6: Channel Gateway** com sessões e roteamento para **Agente de Suporte** e **Chatbot do Cliente**.
- **F7: Allowlist de tools por agente** e limites de escopo por role.

### 3.2 Não funcionais (Qualidades)
- NFR‑SLA: p95 < 800 ms por tool de leitura; criação < 2 s.
- NFR‑Segurança: mTLS, Vault/KMS, tokens curtos, least privilege, logs imutáveis.
- NFR‑Escala: >500k companies, multi‑pod, cache quente.
- NFR‑Confiabilidade: retries exponenciais, idempotência em `create_*`.
- NFR‑Observabilidade: métricas, tracing distribuído, alertas SLO.
- **NFR‑Segregação por agente**: políticas, prompts e quotas isoladas por agente.

## 4. Modelo de segurança
- **Auth**: OIDC Keycloak. Validação `iss/aud/exp/nbf` e JWKS.
- **RBAC**: roles→scopes por tool (`nodes:read`, `incidents:create`, ...).
- **ABAC**: escopo companies do usuário. Se `all`, agrega todas do tenant; senão subset.
- **Defesa em profundidade**: MCP injeta `X-Tenant-ID`, `X-User-Sub`, `X-Roles`, `X-Correlation-ID`; gateways revalidam; backends com contas técnicas por tenant.

## 5. Domínio e dados
- Entidades: Tenant, Company (ITSM `company_sys_id`), Node, Incident, WorkInfo.
- Tabelas núcleo (Postgres):
  - `tenant_company_map(tenant_id BIGINT, company_sys_id TEXT, company_name TEXT, system TEXT, PRIMARY KEY(tenant_id, company_sys_id, system))`
  - `policy_cache(tenant_id, subject_sub, companies_json, roles, ttl)`
- Metadados nos índices RAG (se houver): `tenant_id`, `company_sys_id`, `sensitivity`.

## 6. Integrações
- **MCP → apigateway_solarwinds** (HTTP/mTLS). Tools de leitura e update CP.
- **MCP → gateway ITSM** (HTTP/mTLS). CRUD de incident/work info.
- **ETL**: ITSM API → Loader → Postgres → Update CP no SolarWinds via gateway.

## 7. Padrões de implementação
- **MCP**: fastmcp (Python). Schemas estritos. Versionamento `/v1`.
- **Gateways**: FastAPI. Timeouts, retries, circuit breaker.
- **Queries**: sempre parametrizadas. Sem concatenação.
- **Idempotência**: chave de dedupe em `create_*`.
- **Agents**:
  - **Suporte**: prompt com *system policies*, RAG interno, tools amplas; requer 2‑step para ações destrutivas.
  - **Cliente**: prompt minimalista, sem RAG amplo por padrão, apenas tools de leitura e ações whitelisted; respostas com proveniência.
- **Channel Gateway**: controle de sessão, *tool router* por agente, *content filters* e rate‑limit por tenant.

## 8. Implantação
- K8s. Pods: MCP, gateways, ETL worker. Postgres (HA) + Redis (cache).
- Segredos: HashiCorp Vault ou KMS do provedor.
- Observabilidade: Prometheus, Loki, Tempo/OTel, dashboards por tool/tenant.

## 9. Operação e governança
- **Rotina ETL**: diário + on‑demand. Reconciliadores e relatórios de divergência.
- **Auditoria**: trilha por chamada; retenção legal.
- **Gestão de acessos**: roles no Keycloak; revisão trimestral.

## 10. Riscos e mitigação
- Divergência ITSM↔SolarWinds → reconciliadores e alertas.
- Escala de companies → índice composto + cache Redis; possível sharding.
- Exfiltração via prompt/tool → pré‑filtros mandatórios e allowlist de tools.

## 11. Roadmap (MVP → Fase 2)
- **MVP (60–90 dias)**: Auth, MCP v1, tools core, Postgres map, ETL básico, filtros, auditoria.
- **Fase 2**: Redis cache, account limitation nativa no Orion/equivalente, migração Remedy→ServiceNow via adapter.
- **Fase 2b – Camada de Agentes/RAG (opcional neste ADD)**:
  - RAG multi‑tenant com **pré‑filtro por `tenant_id`/`company_sys_id`** no índice.
  - Cache de respostas por tenant, proveniência obrigatória.
  - Guardrails de tool‑use e quota por tenant.

## 12. Anexos
- Esquemas JSON das tools v1.
- Exemplos de cabeçalhos e contratos.
- Diagramas lógicos (a adicionar).
- **Nota**: A especificação detalhada de Agentes/RAG pode ser entregue como **documento separado** (Anexo A) ou incorporada na Fase 2b, mantendo este ADD focado no core MCP.

