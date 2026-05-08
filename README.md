# Agente de Cliente Desafiador para Treinamento de Vendedores de Consórcios

Um agente conversacional que simula clientes reais com objeções variadas para treinar vendedores de consórcios imobiliários.

## ✨ Características

- **Simulação Realista**: O agente finge ser um cliente genuíno, nunca revela ser IA
- **Objeções Estruturadas**: 50 objeções em 10 categorias (financeiras, operacionais, comportamentais, etc.)
- **Perfis de Cliente Variados**: 3 tipos de perfil com comportamentos distintos:
  - Investidor Analítico (foco em ROI e comparativos)
  - Comprador de Imóvel (foco em segurança e entrada)
  - Perdido/Indeciso (muitas perguntas, pula de tema)
- **Avaliação Automática**: Detecta objeções contornadas vs. não contornadas
- **Análise de Técnicas**: Identifica técnicas de persuasão usadas
- **Relatórios Detalhados**: Score de desempenho e recomendações
- **Sessões Persistentes**: Retome conversas a qualquer momento

## 🚀 Quick Start

```bash
# 1. Clone ou extraia o projeto
cd agente-consorcio

# 2. Configure o ambiente (veja SETUP.md para detalhes)
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt

# 3. Configure a chave da API
cp .env.example .env
# Edite .env e adicione sua ANTHROPIC_API_KEY

# 4. Comece uma nova simulação
python main.py nova --perfil investment-focused
```

## 📖 Uso

### Iniciar nova simulação
```bash
python main.py nova --perfil <nome-do-perfil>
```

Perfis disponíveis: `investment-focused`, `home-buyer`, `undecided`

O agente começará a conversa, apresentando a primeira objeção. Você responde como um vendedor de consórcios.

### Retomar simulação existente
```bash
python main.py retomar --id <session-id>
```

Continua de onde parou na sessão anterior.

### Ver relatório de desempenho
```bash
python main.py relatorio --id <session-id>
```

Mostra análise detalhada com:
- Objeções contornadas vs. não contornadas
- Score final em %
- Técnicas detectadas
- Recomendações de melhoria

### Listar todas as simulações
```bash
python main.py listar
```

Mostra tabela com todas as sessões salvas.

### Listar perfis disponíveis
```bash
python main.py perfis
```

### Deletar simulação
```bash
python main.py deletar --id <session-id>
```

## 🏗️ Arquitetura

```
agente-consorcio/
├── main.py                    # Ponto de entrada
├── src/
│   ├── cli.py                # Interface de linha de comando
│   ├── models.py             # Modelos Pydantic
│   ├── session_manager.py    # Persistência de sessões
│   ├── objection_bank.py     # Banco de objeções
│   ├── profile_system.py     # Sistema de perfis
│   ├── objection_selector.py # Seleção inteligente de objeções
│   ├── claude_agent.py       # Integração com Claude API
│   ├── evaluator.py          # Avaliação de respostas
│   └── report_generator.py   # Geração de relatórios
├── profiles/                 # Definições de perfis JSON
├── objections.json           # Banco de 50 objeções
├── sessions/                 # Históricos de sessões (JSON)
├── tests/                    # Suite de testes
├── requirements.txt          # Dependências Python
├── .env.example             # Exemplo de configuração
└── README.md                # Este arquivo
```

## 🔧 Estrutura de Dados

### Objeção
```json
{
  "id": "taxa_administrativa",
  "categoria": "financeiro",
  "objeção": "Qual é a taxa administrativa mensal?",
  "variações": ["Ouvi dizer que cobram uma taxa mensal alta..."],
  "técnicas_esperadas": ["explicar_competitividade", "comparar_com_alternativas"],
  "dificuldade": 2
}
```

### Sessão
```json
{
  "id": "session-001",
  "profile": "investment-focused",
  "created_at": "2026-05-07T10:30:00",
  "messages": [...],
  "objections_used": [...]
}
```

## 📊 Fluxo de uma Sessão

1. Você inicia: `python main.py nova --perfil investment-focused`
2. O agente se apresenta com a primeira objeção incorporada naturalmente
3. Você responde como vendedor
4. O sistema avalia se você contornou a objeção
5. O agente seleciona a próxima objeção baseado no perfil
6. Loop continua até completar 10 objeções ou você sair (comando `quit`)
7. Relatório é salvo automaticamente
8. Você pode ver o relatório com: `python main.py relatorio --id session-001`

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Verbose
pytest -v

# Teste específico
pytest tests/test_models.py -v
```

Cobertura de testes:
- ✅ Modelos de dados
- ✅ Persistência de sessões
- ✅ Banco de objeções
- ✅ Sistema de perfis
- ✅ Seleção de objeções
- ✅ Integração com Claude API (mocked)
- ✅ Avaliação de respostas
- ✅ Geração de relatórios
- ✅ Interface CLI

## 🔑 Variáveis de Ambiente

```env
ANTHROPIC_API_KEY=sk-ant-...
```

Obtenha uma chave em: https://console.anthropic.com/

## 📝 Exemplos de Conversa

### Perfil: Investidor Analítico

```
Agente: "Oi! Tudo bem? Fiquei sabendo que você vende consórcios. 
Sou bem analítico com investimentos, qual é a taxa administrativa mensal?"

Vendedor: "A taxa é 2% e é bem competitiva comparado com o mercado."

Agente: "Entendo, mas comparando com ações, lá é muito mais barato..."

Vendedor: "Verdade, mas consórcio é um produto diferente com segurança..."
```

### Perfil: Comprador de Imóvel

```
Agente: "Oi! Estou procurando jeitar de juntar uma entrada para comprar 
meu próprio imóvel. Mas tenho medo de perder o sorteio e não conseguir."

Vendedor: "Não precisa confiar só no sorteio. Você pode participar do 
sistema de lance também, com mais possibilidades..."
```

## 🚧 Limitações (MVP)

- Sem dashboard visual (fase 2)
- Sem comparação entre múltiplos vendedores
- Sem histórico agregado de treinamentos
- Sem integração com CRM/WhatsApp

## 🔮 Roadmap

**Fase 2:**
- Web app com histórico visual
- Dashboard comparando múltiplas sessões
- Filtros por perfil, data, desempenho
- Export de relatórios (PDF)

## 📧 Suporte

Para dúvidas ou feedback sobre o agente, entre em contato com a equipe de desenvolvimento.

## 📄 Licença

Todos os direitos reservados.

---

**Desenvolvido com ❤️ para melhorar o treinamento de vendedores de consórcios**
