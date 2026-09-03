# WPN Gestão de Obras

Sistema web para gestão de construtora, desenvolvido com Django.
O aplicativo reúne e centraliza o gerenciamento de obras, clientes, oportunidades comerciais, funcionários, controles financeiros, orçamentos, estoque de materiais e controle de ponto.

## Tecnologias

- **Backend:** Python 3.12, Django 6.1
- **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção)
- **Frontend:** Django Templates (HTML/CSS/JS)

## Como rodar o projeto localmente (Desenvolvimento)

O projeto requer a configuração das variáveis de ambiente de segurança para ser executado.

### 1. Preparar o ambiente e instalar dependências

```bash
# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale os pacotes
pip install -r requirements.txt
```

### 2. Configurar as Variáveis de Ambiente

Crie o arquivo base copiando o exemplo e certifique-se de ativar o modo de debug:

```bash
cp .env.example .env
export DJANGO_DEBUG=True
```
*(Nota: No Linux/Mac, exporte `DJANGO_DEBUG` diretamente no terminal durante o desenvolvimento, ou instale ferramentas como `python-dotenv`).*

### 3. Banco de Dados e Execução

```bash
# Execute as migrações (Cria o db.sqlite3)
python manage.py migrate

# Crie um usuário administrador para acessar o sistema
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver 127.0.0.1:8000
```
Acesse no navegador: **http://127.0.0.1:8000/**

---

## Como rodar usando Docker (Produção / Homologação)

O projeto possui suporte nativo ao Docker Compose empacotado com PostgreSQL.

1. Copie o arquivo de configuração:
```bash
cp .env.example .env
```
2. Modifique as senhas no arquivo `.env` gerado.
3. Suba os containers:
```bash
docker compose up --build -d
```
O servidor estará acessível em `http://127.0.0.1:8000/`.

---

## Pipeline comercial

O módulo **Oportunidades** organiza o ciclo comercial antes da obra: novo contato, visita técnica, orçamento, negociação, aprovado ou perdido. Cada oportunidade fica vinculada a um cliente e registra origem, valor estimado, previsão de fechamento e motivo da perda.

O acesso é controlado pelas permissões padrão do Django (`view_oportunidade`, `add_oportunidade`, `change_oportunidade` e `delete_oportunidade`). Configure grupos e usuários pelo `/admin/`. O relacionamento entre clientes, oportunidades, orçamentos e obras está documentado em [docs/DIAGRAMA.md](docs/DIAGRAMA.md).

As próximas entregas estão organizadas, em ordem de prioridade, em [docs/ROADMAP.md](docs/ROADMAP.md). Cada tarefa define seus testes obrigatórios e a atualização de diagrama necessária.

## Importação e Exportação (CSV e PDF)

Os módulos **Financeiro**, **Orçamentos** e **Materiais** suportam importação de CSV.
- O arquivo deve estar em UTF-8, possuir a primeira linha com cabeçalhos e separar dados por vírgula.
- Exemplo para Financeiro: `valor,data,descricao,tipo,categoria`

Exportações estão disponíveis nos formatos **CSV** e **PDF**, com sanitização nativa contra vulnerabilidades de Formula Injection (CSV Injection).

## Segurança (SecOps)

## Workflows do GitHub

O repositório executa automaticamente:

- CI em push e pull request para `main` e `master`, com `check`, migrações, testes, `pip-audit` e validação do Docker Compose.
- CodeQL em push, pull request e semanalmente para análise estática de Python.
- Dependabot semanal para dependências Python e mensal para GitHub Actions.

Este projeto passou por auditorias de segurança e possui os seguintes controles ativados:
- Timeout absoluto de sessões inativas.
- Proteção contra IP Spoofing na tabela de Auditoria.
- Rate Limiting e prevenção a ataques de Força Bruta (Brute-Force) na página de Login.
- Bypass de Erros Críticos via manipulação de URL (`get_object_or_404`).
- Tratamento e escape para SQL/CSV/XSS.
