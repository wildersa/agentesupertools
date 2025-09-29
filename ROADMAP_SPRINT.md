# Roadmap Sprint - Agente Super Tools (2 Semanas)

## 🎯 Objetivo: DEMONSTRAR que funciona, não produção

**Premissa**: 1 dev experiente, foco em demo funcional, sem over-engineering.

---

## 📅 Sprint de 2 Semanas

### Semana 1: Core MVP (Chat + Observability)

#### Dia 1-2: Setup Mínimo
- [ ] Docker Compose básico (Postgres, Redis)
- [ ] Estrutura de pastas simples
- [ ] FastAPI básico para todos os serviços
- **Tempo**: 4-6 horas

#### Dia 3-4: MCP Broker + Observability
- [ ] MCP server básico com fastmcp
- [ ] Tool `get_metrics` que retorna dados fake
- [ ] Tool `search_assets` com lista hardcoded
- [ ] Adapter observability mockado (em memória)
- **Tempo**: 8-12 horas

#### Dia 5: Agent + Gateway  
- [ ] Agent com classificação de intent simples (if/else)
- [ ] Channel Gateway que aceita POST e chama agent
- [ ] Integração end-to-end funcionando
- **Tempo**: 6-8 horas

**🎯 Entrega Semana 1**: Chat pergunta "CPU servidor X" → resposta com dados fake

### Semana 2: ITSM + Polish

#### Dia 6-7: ITSM Mockado
- [ ] Adapter ITSM com dados em memória
- [ ] Tools `create_incident`, `get_incident`, `update_incident`
- [ ] Integração com observability (enrichment básico)
- **Tempo**: 8-10 horas

#### Dia 8-9: Refinamentos
- [ ] Melhorar parsing de intents
- [ ] Adicionar mais casos de uso
- [ ] Error handling básico
- [ ] Logs estruturados
- **Tempo**: 6-8 horas

#### Dia 10: Demo Ready
- [ ] Testes manuais de todos os fluxos
- [ ] Documentação da demo
- [ ] Scripts para subir ambiente
- [ ] Preparar apresentação
- **Tempo**: 4-6 horas

**🎯 Entrega Semana 2**: Demo completa funcionando

---

## 🔥 O que CORTAR para 2 semanas:

### ❌ Fora do Sprint:
- Keycloak (usar bearer token fixo)
- Postgres complexo (SQLite ou em memória)
- RLS e multi-tenancy real
- Cache inteligente (Redis apenas para rate limit)
- Métricas e observabilidade
- Testes unitários
- Error handling robusto
- Performance otimizada
- Deploy automatizado

### ✅ Manter no Sprint:
- MCP funcionando
- Chat basic flow
- Observability mock
- ITSM mock  
- Integração end-to-end
- Demo convincente

---

## 🛠️ Stack Simplificada para Sprint:

**Backend**: FastAPI + SQLAlchemy + SQLite
**MCP**: fastmcp com tools básicas
**Auth**: Bearer token hardcoded
**Cache**: Redis para rate limit básico
**Deploy**: Docker Compose simples
**Data**: JSON files ou in-memory

---

## 🎬 Demo Script (2 semanas):

### Cenário 1: Consulta Observability
```
User: "CPU do servidor web-01"
Bot: "Servidor web-01: CPU 85% (últimos 5min), Memória 62%, Status: WARNING"
```

### Cenário 2: Abrir Incidente
```
User: "Abrir incidente para web-01 com CPU alto"
Bot: "Incidente INC001234 criado. Servidor: web-01, CPU atual: 85%, Status: Aberto"
```

### Cenário 3: Enriquecimento
```
User: "Status do INC001234"
Bot: "INC001234: Aberto, Servidor web-01, CPU agora: 78% (melhorou), Memória: 60%"
```

---

## ⚡ Desenvolvimento Ágil - Dia a Dia:

### Dia 1: "Hello World" End-to-End
- FastAPI rodando
- MCP server responde "pong"
- Chat gateway aceita POST
- **Meta**: Request→Response funcionando

### Dia 2: Primeira Tool
- Tool `ping` funcionando
- Agent chama MCP
- Resposta no chat
- **Meta**: Fluxo completo com dados reais

### Dia 3-4: Observability
- Tools de metrics e assets
- Dados mockados convincentes
- **Meta**: "CPU servidor X" funciona

### Dia 5: Integration Day
- Tudo conectado
- Error handling básico
- **Meta**: Demo Observability pronta

### Dia 6-7: ITSM
- CRUD incidentes
- Enriquecimento básico
- **Meta**: Lifecycle completo incidentes

### Dia 8-9: Polish
- Mais casos de uso
- Melhor UX nas respostas
- **Meta**: Demo convincente

### Dia 10: Demo Prep
- Testes, docs, scripts
- **Meta**: Apresentação pronta

---

## 🎯 Critérios de "Sucesso Sprint":

✅ **Must Have (2 semanas)**:
- Chat responde consultas observability
- Chat cria/atualiza incidentes
- Enriquecimento básico funciona
- Demo end-to-end em < 5 minutos

✅ **Nice to Have**:
- Rate limiting básico
- Logs estruturados
- Error handling decent
- Multi-tenant stub

❌ **Definitivamente Fora**:
- Segurança real
- Performance optimization
- Testes automatizados
- Deploy produção

---

## 💡 Por que 2 semanas É possível:

1. **Foco apenas em demo**, não produção
2. **Mocks everywhere** - sem integrações reais
3. **Arquitetura simples** - sem over-engineering  
4. **Dev experiente** - conhece as libs
5. **Sem scope creep** - features fixas
6. **Dados fake** - sem problemas de integração

## ⚠️ Por que pode virar 6-8 semanas:

1. **Integrações reais** com SolarWinds/ServiceNow
2. **Segurança real** com Keycloak + RBAC
3. **Multi-tenancy** com RLS
4. **Performance** e cache inteligente
5. **Testes** e qualidade produção
6. **Deploy** e operação

---

**Conclusão**: 2 semanas para **DEMO** é totalmente viável! 6-8 semanas para **PRODUÇÃO** é realista.

Qual abordagem você prefere? Sprint de 2 semanas para mostrar que funciona, ou roadmap completo?