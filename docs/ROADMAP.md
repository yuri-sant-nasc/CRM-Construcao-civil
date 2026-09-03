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

**Status:** `CONCLUIDA`

**Objetivo:** acompanhar previsto, realizado, contas a pagar/receber e resultado por obra.

**Entregas realizadas:** vencimento, pagamento parcial, status financeiro, centro de custo, saldo aberto, filtros por obra/status e permissões para lançamento.

**Entregas realizadas:** vencimento, pagamento parcial, status financeiro, centro de custo, saldo aberto, filtros por obra/status, permissões para lançamento e painel gerencial com previsto versus realizado por obra.

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

### UX/UI e experiencia operacional

As tarefas desta frente devem ser executadas junto das funcionalidades correspondentes. Toda alteracao visual deve ser validada em desktop e mobile, com dados longos, estados vazios, erros e permissoes reduzidas.

#### UX01 - Navegacao orientada ao trabalho

**Status:** `PENDENTE`

**Objetivo:** reduzir o tempo para chegar a clientes, oportunidades, obras e pendencias.

**Entregas:** menu agrupado por Comercial, Obras, Financeiro e Cadastros; destaque da pagina atual; breadcrumb nas telas internas; acesso rapido a busca e tarefas; navegacao adequada para telas pequenas.

**Testes obrigatorios:** todos os links funcionam, rota atual fica identificada, usuario sem permissao nao ve atalhos indevidos, teclado percorre a navegacao e layout nao cria rolagem horizontal em 320px.

**Diagrama:** nao altera entidades; se houver nova busca ou notificacao, atualizar as tarefas T11/T12.

#### UX02 - Dashboard para decisao da construtora

**Status:** `PENDENTE`

**Objetivo:** apresentar rapidamente o que exige acao hoje.

**Entregas:** cards de obras atrasadas, oportunidades por etapa, contas proximas do vencimento, estoque critico e atividades recentes; filtros persistentes por periodo, obra e responsavel; estados vazios explicativos.

**Testes obrigatorios:** totais batem com a base, filtros combinam corretamente, valores monetarios usam formato brasileiro, dados nao aparecem sem permissao e componentes funcionam em mobile.

**Diagrama:** nao altera entidades; documentar as fontes dos indicadores em T13.

#### UX03 - Listas, busca e filtros operacionais

**Status:** `PENDENTE`

**Objetivo:** facilitar comparacao e localizacao de registros no trabalho diario.

**Entregas:** busca visivel, filtros por status/obra/responsavel/periodo, ordenacao, paginacao, colunas responsivas, acao em lote somente onde fizer sentido e preservacao dos filtros ao voltar.

**Testes obrigatorios:** busca sem resultado, muitos registros, filtros combinados, paginacao, consulta com caracteres especiais, permissao e viewport mobile.

**Diagrama:** nao altera entidades; novos indices devem ser documentados em T12.

#### UX04 - Formulario de cadastro sem retrabalho

**Status:** `PENDENTE`

**Objetivo:** reduzir erros de cadastro de clientes, obras, oportunidades e orcamentos.

**Entregas:** campos agrupados por contexto, obrigatorios identificados, mascaras para CPF/CNPJ/telefone/moeda, ajuda contextual, validacao proxima ao campo, preservacao dos dados apos erro e confirmacao antes de exclusao.

**Testes obrigatorios:** erros por campo, valores invalidos, teclado, leitores de tela, envio duplicado, perda de sessao e validacao server-side equivalente.

**Diagrama:** nao altera entidades; alterações de campos exigem atualização do diagrama e migração.

#### UX05 - Operacao de obra em campo

**Status:** `PENDENTE`

**Objetivo:** permitir uso rapido no celular durante a visita ou execução da obra.

**Entregas:** painel da obra com status e progresso em destaque, diario com poucos passos, captura de foto pelo celular, ocorrencia com prioridade, leitura adequada sob luz forte e botoes grandes para toque.

**Testes obrigatorios:** viewport 320px/390px, upload por camera, conexao lenta, falha de upload sem perder texto, toque sem sobreposicao e permissao por perfil.

**Diagrama:** nao altera entidades; o armazenamento de fotos segue T15 e deve atualizar o diagrama de infraestrutura.

#### UX06 - Orcamento legivel para cliente e equipe

**Status:** `PENDENTE`

**Objetivo:** tornar custos e margem compreensiveis sem expor informacao indevida.

**Entregas:** resumo financeiro destacado, composicao por categoria, diferenca entre custo e preco de venda, comparacao de versoes, preview da proposta e PDF com identidade visual consistente.

**Testes obrigatorios:** arredondamento, totais, versoes, PDF em A4 e mobile, dados do cliente corretos e ausencia de custo interno quando a proposta for externa.

**Diagrama:** atualiza entidades apenas quando houver novos campos de apresentacao ou versao; manter T03 e DIAGRAMA.md sincronizados.

#### UX07 - Feedback, estados e recuperacao de erro

**Status:** `PENDENTE`

**Objetivo:** deixar claro o resultado de cada acao e como continuar quando algo falhar.

**Entregas:** mensagens de sucesso/erro consistentes, loading em operacoes demoradas, estados vazios, confirmacao de exclusao, pagina de erro amigavel, retry seguro e identificador para suporte.

**Testes obrigatorios:** sucesso, erro de validacao, timeout, falha de permissao, envio repetido, resposta 404/500 e mensagens acessiveis por leitor de tela.

**Diagrama:** nao altera entidades; incidentes e logs devem ser cobertos por T17.

#### UX08 - Acessibilidade e consistencia visual

**Status:** `PENDENTE`

**Objetivo:** tornar o sistema utilizavel por diferentes perfis, dispositivos e capacidades.

**Entregas:** contraste adequado, foco visivel, hierarquia de headings, labels associados, textos alternativos, navegação por teclado, componentes reutilizaveis e tokens de cor/espacamento.

**Testes obrigatorios:** axe ou equivalente, teclado sem mouse, zoom 200%, contraste, leitor de tela basico e navegadores suportados.

**Diagrama:** nao altera entidades.

#### UX09 - Validacao com usuarios da construcao civil

**Status:** `PENDENTE`

**Objetivo:** validar a interface com quem vende, gerencia e executa obras.

**Entregas:** roteiros para comercial, engenheiro/mestre, financeiro e almoxarifado; testes moderados; registro de problemas por gravidade; revisao apos cada entrega.

**Testes obrigatorios:** pelo menos um cenario real por perfil, medicao de tempo, taxa de conclusao, erros observados e aceite dos fluxos criticos.

**Diagrama:** nao altera entidades; descobertas que mudarem o dominio devem abrir tarefa de modelo e atualizar DIAGRAMA.md.

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
