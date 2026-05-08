# Setup & Installation Guide

Guia detalhado para configurar o Agente de Cliente Desafiador em sua máquina.

## 📋 Pré-requisitos

- **Python 3.9+** (recomendado 3.12+)
- **pip** (gerenciador de pacotes Python)
- **Chave da API Anthropic** (obtida em https://console.anthropic.com/)
- **Git** (opcional, mas recomendado)

## 🔍 Verificar Python

```bash
python --version
```

Se você não tem Python 3.9+, baixe em: https://www.python.org/downloads/

### Windows
```bash
# PowerShell
python -V

# Se python não funcionar, tente:
py -3.12
```

### macOS/Linux
```bash
python3 --version
```

## 🛠️ Instalação Passo a Passo

### 1. Clone ou Extraia o Projeto

**Via Git:**
```bash
git clone <url-do-repositorio>
cd agente-consorcio
```

**Via Download:**
- Extraia o arquivo `.zip` em seu local desejado
- Abra um terminal na pasta do projeto

### 2. Crie um Ambiente Virtual

Um ambiente virtual isola as dependências do projeto.

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você deve ver `(venv)` no início do seu prompt do terminal.

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

Isso instala:
- `anthropic` — SDK para Claude API
- `pydantic` — Validação de dados
- `typer` — Interface CLI
- `rich` — Formatação de terminal
- `python-dotenv` — Gerenciamento de variáveis de ambiente
- `pytest` — Framework de testes

**Verificar instalação:**
```bash
pip list
```

### 4. Configure a Chave da API

#### Obter a Chave

1. Acesse: https://console.anthropic.com/
2. Faça login com sua conta
3. Vá para "API Keys"
4. Clique em "Create Key"
5. Copie a chave gerada (começa com `sk-ant-`)

#### Adicionar ao Projeto

**Opção A: Arquivo `.env` (Recomendado)**

```bash
# Copie o exemplo
cp .env.example .env

# Ou crie um novo arquivo .env
```

Edite `.env` com um editor de texto:
```env
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

**Opção B: Variável de Ambiente do Sistema**

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-sua-chave-aqui"
```

**Windows (CMD):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

### 5. Verifique a Instalação

```bash
# Tente ver a ajuda
python main.py --help

# Ou liste os perfis
python main.py perfis
```

Se funcionar, a instalação está completa!

## ✅ Checklist de Setup

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado (`venv`)
- [ ] Ambiente virtual ativado (vê `(venv)` no prompt?)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado com `ANTHROPIC_API_KEY`
- [ ] `python main.py perfis` funciona sem erro

## 🧪 Rodar Testes (Opcional)

Verificar se tudo está funcionando:

```bash
# Todos os testes
pytest

# Com mais detalhes
pytest -v

# Apenas um arquivo
pytest tests/test_models.py -v
```

Esperado: **Todos os testes PASSAM**

## 🎯 Primeiro Uso

Após setup completo, comece uma simulação:

```bash
python main.py nova --perfil investment-focused
```

Você verá:
```
[✓] Iniciando sessão: session-001
[✓] Perfil: Investidor Analítico

Agente: "Oi! Tudo bem? Você trabalha com consórcios..."

Você: [sua resposta aqui]
> 
```

Digite sua resposta e pressione Enter.

Para sair: digite `quit`

## 🔧 Troubleshooting

### "python: command not found"

Python não está instalado ou não está no PATH.

**Solução:**
- Baixe Python: https://www.python.org/downloads/
- Marque "Add Python to PATH" durante instalação
- Reinicie o terminal

### "ANTHROPIC_API_KEY not set"

A chave da API não foi configurada.

**Solução:**
1. Crie arquivo `.env` na raiz do projeto
2. Adicione: `ANTHROPIC_API_KEY=sk-ant-sua-chave`
3. Salve o arquivo
4. Reinicie o terminal

### "ModuleNotFoundError: No module named 'anthropic'"

As dependências não foram instaladas.

**Solução:**
```bash
# Certifique-se de estar no diretório correto
cd agente-consorcio

# Ative o ambiente virtual
source venv/Scripts/activate  # Windows
source venv/bin/activate      # macOS/Linux

# Instale as dependências
pip install -r requirements.txt
```

### "No sessions found" ao rodar `listar`

Nenhuma simulação foi iniciada ainda.

**Solução:**
Crie uma nova simulação:
```bash
python main.py nova --perfil investment-focused
```

### Erro de permissão no Windows

Se tiver erro ao ativar o venv.

**Solução:**
```powershell
# Execute PowerShell como administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Outro Erro?

Verifique:
1. Python versão: `python --version` (deve ser 3.9+)
2. Ambiente virtual ativado: vê `(venv)` no prompt?
3. Arquivo `.env` existe e tem a chave?
4. Testes passam: `pytest -v`

## 📁 Estrutura de Pastas

Após setup, você terá:

```
agente-consorcio/
├── venv/                    ← Ambiente virtual (pode ignorar)
├── src/                     ← Código-fonte
├── tests/                   ← Testes
├── profiles/                ← Definições de perfis
├── sessions/                ← Sessões salvas (criado automaticamente)
├── main.py                  ← Ponto de entrada
├── objections.json          ← Banco de objeções
├── requirements.txt         ← Dependências
├── .env                     ← Variáveis de ambiente (não commitar!)
├── .gitignore              ← Arquivos ignorados pelo Git
├── README.md               ← Documentação geral
└── SETUP.md                ← Este arquivo
```

## 🔐 Segurança

**⚠️ Nunca compartilhe sua `ANTHROPIC_API_KEY`**

- Não commite `.env` para Git (já está em `.gitignore`)
- Não copie a chave em mensagens ou documentos
- Se vazar, revogue em https://console.anthropic.com/

## 🚀 Próximos Passos

1. Leia [README.md](README.md) para entender melhor o projeto
2. Comece uma simulação: `python main.py nova --perfil investment-focused`
3. Experimente os diferentes perfis
4. Veja relatórios: `python main.py relatorio --id <session-id>`

## 💾 Dados Persistidos

As sessões são salvas em `sessions/` como arquivos JSON. Você pode:
- **Retomar**: `python main.py retomar --id session-001`
- **Ver relatório**: `python main.py relatorio --id session-001`
- **Deletar**: `python main.py deletar --id session-001`

Não há banco de dados — tudo é em JSON para simplicidade.

## 📞 Suporte

Se encontrar problemas:
1. Verificar este guia (seção Troubleshooting)
2. Rodar testes: `pytest -v`
3. Verificar logs do console
4. Entre em contato com a equipe

---

**Setup concluído com sucesso! 🎉**

Você está pronto para começar a treinar vendedores com o agente.
