# Roadmap do CRM para construcao civil

Este roadmap transforma as melhorias do CRM em tarefas independentes. Execute uma tarefa por vez, marque-a como concluida somente depois dos testes e atualize o diagrama indicado na propria tarefa.

## Regras de execucao

- Status inicial das tarefas novas: `PENDENTE`.
- Toda tarefa deve incluir testes automatizados e validacao manual do fluxo.
- Toda mudanca de modelo ou relacionamento deve atualizar [DIAGRAMA.md](DIAGRAMA.md).
- Toda tarefa concluida deve registrar uma migracao, quando aplicavel, e passar por `python manage.py test`.
- Nao colocar dados reais, senhas ou documentos de clientes no repositorio.

## Ordem de implementacao

### Alta prioridade

#### T01 - Completar pipeline comercial

**Status:** `CONCLUIDA`

**Objetivo:** conectar cliente, oportunidade, proposta/orcamento e obra em um fluxo comercial rastreavel.

**Entregas realizadas:** responsavel comercial, probabilidade de fechamento, proximo contato, historico de etapas, conversao unica para orcamento e motivo obrigatorio para oportunidades perdidas.

**Testes obrigatorios:**

- Criar, editar, filtrar e excluir oportunidade.
- Impedir etapa `perdido` sem motivo.
- Converter oportunidade em orcamento uma unica vez.
- Garantir permissoes por grupo e isolamento de dados.

**Diagrama:** atualizar `CLIENTE`, `OPORTUNIDADE` e `ORCAMENTO` em [DIAGRAMA.md](DIAGRAMA.md).

#### T02 - Gestao completa de obras

**Status:** `CONCLUIDA`

**Objetivo:** transformar `Obra` em centro operacional da construcao.

**Entregas realizadas:** responsavel, equipe, percentual concluido, diario de obra, ocorrencias e fotos com extensao e tamanho validados.

**Entregas realizadas:** painel operacional por obra, registro de diario e ocorrencias, upload de fotos e download autorizado.

**Entregas realizadas:** painel operacional por obra, filtros por status e responsável, regra de conclusão com 100%, registro de diário e ocorrências, upload de fotos e download autorizado.

**Testes obrigatorios:** validacao de percentuais e datas, transicoes de status, permissao de acesso, upload seguro de imagens e limite de tamanho.

**Diagrama:** adicionar `USUARIO`, `DIARIO_OBRA`, `OCORRENCIA` e `FOTO_OBRA` ligados a `OBRA`.

#### T03 - Orcamento detalhado

**Status:** `CONCLUIDA`

**Objetivo:** decompor cada orcamento em materiais, mao de obra, equipamentos e servicos.

**Entregas realizadas:** itens de orçamento por categoria, quantidade, custo unitário, margem, totais calculados e proposta PDF protegida por permissão.

**Entregas realizadas:** itens de orçamento por categoria, quantidade, custo unitário, margem, totais calculados, proposta PDF, reajuste transacional e histórico versionado com snapshot dos itens.

**Testes obrigatorios:** calculos monetarios com `Decimal`, totais, margem, validacao de valores negativos, permissao e PDF sem dados de outra obra.

**Diagrama:** adicionar `ITEM_ORCAMENTO` e `CATEGORIA_CUSTO` ligados a `ORCAMENTO`.

#### T04 - Financeiro por obra

**Status:** `PENDENTE`

**Objetivo:** acompanhar previsto, realizado, contas a pagar/receber e resultado por obra.

**Entregas:** vencimento, pagamento parcial, status financeiro, centro de custo e indicadores por obra.

**Testes obrigatorios:** saldo por obra, vencimentos, pagamentos parciais, filtros de periodo, valores monetarios e isolamento por permissao.

**Diagrama:** adicionar `CONTA_FINANCEIRA` e `PAGAMENTO` ligados a `OBRA` e `TRANSACAO`.

#### T05 - Perfis de acesso por funcao

**Status:** `PENDENTE`

**Objetivo:** aplicar menor privilegio para administrador, comercial, gestor de obra e financeiro/almoxarifado.

**Entregas:** grupos configuraveis, matriz de permissoes, menu condicional e protecao server-side para cada acao.

**Testes obrigatorios:** cada perfil deve passar apenas nas rotas permitidas; acesso direto proibido deve retornar `403`; exportacoes e importacoes tambem devem ser cobertas.

**Diagrama:** nao altera entidades; documentar os perfis e permissoes em [COMPLIANCE.md](COMPLIANCE.md).

### Media prioridade

#### T06 - Agenda de visitas, reunioes e tarefas

**Status:** `PENDENTE`

**Entregas:** compromissos vinculados a cliente/oportunidade/obra, responsavel, prazo, status e lembretes.

**Testes obrigatorios:** criacao, conflito de horario, filtros, permissao e tarefas vencidas.

**Diagrama:** adicionar `ATIVIDADE` ligada a `CLIENTE`, `OPORTUNIDADE`, `OBRA` e `USUARIO`.

#### T07 - Fornecedores e subempreiteiros

**Status:** `PENDENTE`

**Entregas:** cadastro, categorias, documentos, contratos, validade e avaliacao.

**Testes obrigatorios:** unicidade de documentos, validacao de vencimento, permissao e busca.

**Diagrama:** adicionar `FORNECEDOR`, `SUBEMPREITEIRO` e `CONTRATO`.

#### T08 - Estoque por obra

**Status:** `PENDENTE`

**Entregas:** entradas, saidas, transferencias, reserva e consumo por obra, com responsavel.

**Testes obrigatorios:** estoque nunca negativo, concorrencia/transacao, movimentacoes auditadas e saldo por obra.

**Diagrama:** adicionar `MOVIMENTACAO_ESTOQUE` e `ALOCACAO_ITEM`.

#### T09 - Medicao de servicos

**Status:** `PENDENTE`

**Entregas:** servico contratado, quantidade prevista/executada, aprovacao e vinculo com financeiro.

**Testes obrigatorios:** calculos, limites, aprovacao por perfil, reprovacao e reflexo no custo realizado.

**Diagrama:** adicionar `SERVICO`, `MEDICAO` e `ITEM_ORCAMENTO`.

#### T10 - Documentos e conformidade da obra

**Status:** `PENDENTE`

**Entregas:** contratos, ARTs, notas fiscais, licencas, validade, versionamento e acesso restrito.

**Testes obrigatorios:** extensoes permitidas, tamanho, nome seguro, download autorizado, bloqueio de acesso e expiracao.

**Diagrama:** adicionar `DOCUMENTO` ligado a `CLIENTE`, `OBRA`, `FORNECEDOR` e `USUARIO`.

#### T11 - Alertas e notificacoes

**Status:** `PENDENTE`

**Entregas:** alertas de vencimentos, pagamentos, estoque minimo, atrasos e tarefas; preferencia por usuario.

**Testes obrigatorios:** regras de disparo, nao duplicacao, destinatarios, timezone e falha do provedor de e-mail.

**Diagrama:** adicionar `NOTIFICACAO` ligada a `USUARIO` e ao registro de origem.

#### T12 - Busca global e filtros

**Status:** `PENDENTE`

**Entregas:** busca por cliente, obra, CPF/CNPJ, endereco, status, responsavel e periodo, com paginacao.

**Testes obrigatorios:** resultados corretos, limites de pagina, consultas vazias, escaping e permissao dos resultados.

**Diagrama:** nao altera entidades; documentar os campos indexados se novos indices forem criados.

#### T13 - Relatorios gerenciais

**Status:** `PENDENTE`

**Entregas:** obras atrasadas, conversao comercial, margem, previsto versus realizado, fluxo de caixa e estoque.

**Testes obrigatorios:** agregacoes comparadas com dados conhecidos, filtros, exportacao e permissao por perfil.

**Diagrama:** nao altera entidades; documentar fontes de cada indicador.

### Qualidade, operacao e seguranca

#### T14 - PostgreSQL, backups e restauracao

**Status:** `PENDENTE`

**Entregas:** PostgreSQL padrao em homologacao, backup automatico criptografado, retencao e teste de restauracao documentado.

**Testes obrigatorios:** migracoes limpas, restauracao em ambiente descartavel e verificacao de integridade.

**Diagrama:** atualizar o contexto de infraestrutura, sem incluir credenciais.

#### T15 - Armazenamento externo de arquivos

**Status:** `PENDENTE`

**Entregas:** armazenamento de fotos/documentos fora do container, URLs protegidas, retencao e limpeza.

**Testes obrigatorios:** upload/download autorizado, falha do storage, limite, tipo MIME e ausencia de caminho previsivel.

**Diagrama:** adicionar `STORAGE` ao diagrama de infraestrutura.

#### T16 - Processamento assincrono

**Status:** `PENDENTE`

**Entregas:** fila para PDFs, importacoes, notificacoes e tarefas periodicas.

**Testes obrigatorios:** idempotencia, retry, falha parcial, status da tarefa e autorizacao do resultado.

**Diagrama:** adicionar `WORKER` e `QUEUE` ao diagrama de infraestrutura.

#### T17 - Testes de seguranca e observabilidade

**Status:** `PENDENTE`

**Entregas:** cobertura de autorizacao, CSRF, uploads, rate limit distribuido, logs, alertas e auditoria revisavel.

**Testes obrigatorios:** `check --deploy`, `pip-audit`, testes de permissao para todas as rotas, verificacao de headers e teste de rate limit com cache compartilhado.

**Diagrama:** atualizar o contexto de seguranca, auditoria e observabilidade.

## Criterio de conclusao do roadmap

O roadmap sera considerado concluido quando todas as tarefas estiverem `CONCLUIDA`, os testes automatizados passarem, as migracoes estiverem aplicadas em ambiente de homologacao, os diagramas refletirem os modelos reais e houver evidencia de backup/restauracao e revisao de permissoes.
