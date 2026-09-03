# Controles de seguranca, LGPD e ISO 27001

Este documento registra os controles tecnicos implementados no WPN. Ele nao representa certificacao ISO 27001 nem substitui a adequacao juridica, o registro de tratamento ou a avaliacao de riscos da empresa.

## Controles implementados

- Segredo da aplicacao por `DJANGO_SECRET_KEY`.
- `DEBUG` controlado por `DJANGO_DEBUG` e desligado por padrao.
- Hosts controlados por `DJANGO_ALLOWED_HOSTS`.
- Cookies de sessao e CSRF com atributos de seguranca; em producao, uso de HTTPS.
- Protecao CSRF nos formularios.
- Alteracoes e exclusoes somente por `POST`.
- Limite de tamanho para arquivos enviados.
- Validacao de campos antes da persistencia dos CSVs.
- Trilha de auditoria de operacoes mutaveis com usuario, rota, IP, status e horario.
- Senhas delegadas ao sistema de autenticacao do Django, com validadores ativos.
- Dados de obras, clientes, financeiro e materiais separados por relacionamentos explicitos.

## Checklist LGPD operacional

1. Definir controlador, operador e encarregado de dados.
2. Registrar finalidades e bases legais para clientes e funcionarios.
3. Coletar somente os dados necessarios e revisar os campos de CPF, telefone e endereco.
4. Publicar aviso de privacidade e informar direitos dos titulares.
5. Criar processo para acesso, correcao, eliminacao e portabilidade quando aplicavel.
6. Definir prazos de retencao e descarte seguro.
7. Restringir acesso por funcao e revisar permissoes periodicamente.
8. Registrar e responder incidentes de seguranca.
9. Formalizar contratos e requisitos de seguranca com fornecedores.
10. Fazer backup criptografado, teste de restauracao e controle de acesso ao backup.

## Checklist ISO 27001

- Manter inventario de ativos, dados e dependencias.
- Manter matriz de riscos com responsaveis e tratamento aprovado.
- Revisar logs de auditoria e alertas periodicamente.
- Aplicar atualizacoes e analise de vulnerabilidades.
- Separar ambientes de desenvolvimento, teste e producao.
- Usar PostgreSQL em producao, HTTPS e gerenciamento de segredos.
- Documentar continuidade, recuperacao e resposta a incidentes.
- Treinar usuarios e revisar acessos, especialmente administradores.
- Manter evidencias de testes, backups, revisoes e aprovacoes.

## Variaveis de producao

```text
DJANGO_SECRET_KEY=<segredo-forte-e-privado>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=app.exemplo.com
DJANGO_SECURE_SSL_REDIRECT=True
DATABASE_URL=postgresql://usuario:senha@host:5432/banco
DJANGO_EMAIL_HOST=smtp.exemplo.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_USER=mailer@exemplo.com
DJANGO_EMAIL_PASSWORD=<senha-do-servico-de-email>
```
