Objetivo do projeto:
Plataforma multi-tenant de agentes para Suporte/Cliente que consulta e executa ações em ferramentas de Observabilidade e ITSM via chat/web/app, com isolamento por tenant→company e autorização centralizada.

Funções principais

Consultar monitoramento (SolarWinds e afins) e devolver só os itens do usuário/tenant.

Abrir/atualizar/fechar incidentes no ITSM conforme regras do tenant.

Enriquecer tickets com dados de observabilidade e contexto do ativo.

Orquestrar fluxos entre canais (chat/web/app) e os adapters, com cache e auditoria.

Expor ferramentas ao LLM via MCP, evitando acesso direto às APIs finais.

Componentes do diagrama

Channel Gateway: entrada única dos canais já existentes.

Keycloak: autenticação e emissão de tokens; base para RBAC/ABAC.

Agents Layer: agentes “Suporte” e “Cliente” que chamam ferramentas via MCP.

MCP Broker: roteia chamadas de ferramenta e impõe escopo do token.

Adapters Layer: micro-serviços para Observability e ITSM (traduzem chamadas).

Postgres: modelo tenancy (tenant↔company), políticas de linha e auditoria.

Redis: cache de curto prazo e rate-limit.

Resultados esperados

Segurança por escopo e por linha de dados.

Interoperabilidade com qualquer gateway e qualquer ferramenta plugável.

Menos acoplamento entre canais e backends.

Base pronta para regras finas de permissão e auditoria completa.
