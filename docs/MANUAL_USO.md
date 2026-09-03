# Manual de uso do WPN Gestão de Obras

**Versão:** 1.0  
**Atualizado em:** 2026-09-02  
**Escopo:** funcionalidades disponíveis no sistema nesta versão.

## 1. Visão geral

O WPN é um CRM para construtoras. Ele conecta o relacionamento comercial ao ciclo da obra:

`Cliente -> Oportunidade -> Orçamento -> Obra -> Operação e Financeiro`

O sistema também oferece cadastro de funcionários, controle de faltas e ponto, materiais, importação/exportação e trilha de auditoria.

## 2. Acesso ao sistema

### Ambiente local

1. Ative o ambiente virtual.
2. Execute as migrações.
3. Inicie o servidor.
4. Acesse `http://127.0.0.1:8000/`.

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Faça login com um usuário criado pelo administrador. Usuários não autenticados são encaminhados para a tela de login.

### Administração

Acesse `/admin/` com um usuário administrador. Use o Django Admin para:

- Criar usuários.
- Criar grupos.
- Atribuir permissões.
- Cadastrar ou corrigir dados.
- Consultar registros de auditoria.

## 3. Perfis e permissões

O acesso é controlado por permissões padrão do Django. A recomendação é criar grupos por função:

- **Leitura:** permissões `view_*` dos módulos necessários.
- **Comercial:** clientes e oportunidades; pode receber `add_*` e `change_*` desses modelos.
- **Gestão de obras:** obras, diário, ocorrências e fotos.
- **Financeiro:** transações, pagamentos, orçamentos e relatórios.
- **Almoxarifado:** materiais e movimentações quando esse módulo estiver disponível.
- **Administração:** acesso completo somente para responsáveis autorizados.

A interface oculta atalhos sem permissão, mas a proteção principal ocorre no servidor. Tentar acessar uma rota diretamente sem permissão retorna `403`.

## 4. Clientes

Use **Clientes** para manter o cadastro da pessoa ou empresa contratante.

Fluxo recomendado:

1. Cadastre nome, empresa, contato e documentos.
2. Revise telefone, e-mail e endereço.
3. Salve o cliente.
4. Abra uma oportunidade comercial vinculada a esse cliente.

Evite cadastrar o mesmo cliente mais de uma vez. CPF/CNPJ são campos únicos quando aplicável.

## 5. Oportunidades comerciais

Acesse **Oportunidades** para acompanhar potenciais contratos antes da criação da obra.

### Cadastro

Informe:

- Cliente.
- Responsável comercial.
- Título da oportunidade.
- Origem do contato.
- Valor estimado.
- Probabilidade de fechamento entre 0 e 100%.
- Previsão de fechamento.
- Próximo contato.
- Observações.

### Etapas

- **Novo contato:** oportunidade recém-criada.
- **Visita técnica:** visita ou levantamento em avaliação.
- **Orçamento:** proposta em elaboração ou análise.
- **Negociação:** valores e condições em negociação.
- **Aprovado:** cliente aceitou a oportunidade.
- **Perdido:** negociação encerrada sem contratação.

Ao selecionar **Perdido**, informe obrigatoriamente o motivo. Alterações de etapa são registradas no histórico.

### Conversão em orçamento

Uma oportunidade aprovada pode ser convertida em orçamento pelo botão **Converter em orçamento**. A conversão:

- Cria um orçamento para o mesmo cliente.
- Usa o título como descrição.
- Usa o valor estimado como valor inicial.
- Pode acontecer somente uma vez.
- Exige as permissões `change_oportunidade` e `add_orcamento`.

## 6. Obras

Use **Obras** para acompanhar contratos em execução.

### Cadastro e acompanhamento

Informe cliente, responsável, equipe, endereço, datas, status, percentual concluído e observações.

Os status disponíveis são:

- Planejamento.
- Em andamento.
- Concluída.
- Cancelada.

Uma obra marcada como concluída precisa estar com 100% de conclusão. Use os filtros de status e responsável para localizar obras rapidamente.

### Operação da obra

Abra **Operação** na linha da obra para acessar o painel operacional. Nesse painel é possível:

- Registrar o diário da obra com data e resumo.
- Abrir uma ocorrência com descrição e status.
- Enviar foto da obra.
- Consultar registros recentes.
- Baixar fotos autorizadas.

Fotos aceitas: JPG, JPEG, PNG e WEBP, com limite de 5 MB. O download exige a permissão `view_fotoobra`.

## 7. Orçamentos

Use **Orçamentos** para registrar propostas vinculadas a clientes e, opcionalmente, a obras.

### Composição

Abra **Detalhar** no orçamento para adicionar itens por categoria:

- Material.
- Mão de obra.
- Equipamento.
- Serviço.

Para cada item informe descrição, quantidade, custo unitário e margem. O sistema calcula o total do item e o total da composição.

Valores negativos e quantidades inválidas são rejeitados.

### Reajustes e versões

Na tela de composição, use **Registrar reajuste** para informar percentual e motivo. O sistema:

- Atualiza o valor do orçamento em uma transação.
- Cria uma nova versão numerada.
- Guarda valor anterior e novo.
- Guarda um snapshot dos itens.
- Exibe o histórico de versões.

Use **Gerar proposta PDF** para produzir a proposta da composição. O acesso exige `view_orcamento`.

## 8. Financeiro

Use **Financeiro** para registrar receitas e despesas.

### Transações

Informe valor, data, descrição, tipo, categoria, obra, vencimento, centro de custo e status.

Os status são:

- **Pendente:** nenhum pagamento registrado.
- **Parcial:** parte do valor foi paga.
- **Pago:** o valor total foi quitado.
- **Cancelado:** lançamento cancelado.

Vincule a transação à obra sempre que o lançamento pertencer a um contrato específico.

### Pagamentos parciais

Na listagem financeira, informe o valor no campo de pagamento da transação e clique em **Pagar**. O sistema:

- Impede valores maiores que o saldo aberto.
- Atualiza o status para parcial ou pago.
- Registra data, observação e usuário responsável.

### Painel por obra

Abra **Painel por obra** para consultar, por obra:

- Valor previsto nos orçamentos.
- Receitas.
- Despesas.
- Resultado.
- Saldo previsto.
- Percentual de execução financeira.

É possível filtrar por obra e período.

## 9. Funcionários, faltas e ponto

- **Funcionários:** mantenha equipe, função, documentos e dados de contato.
- **Faltas:** registre data, presença, motivo e justificativa.
- **Ponto:** registre entrada, saída e observação do funcionário.

O acesso a cada área depende das permissões `view_*`, `add_*`, `change_*` e `delete_*` correspondentes.

## 10. Materiais

Use **Materiais** para controlar itens, ferramentas e EPIs, incluindo quantidade disponível, mínimo, fabricante, aquisição, vencimento e obra vinculada.

Quando a quantidade disponível estiver no mínimo ou abaixo dele, o item aparece no alerta de estoque do dashboard.

## 11. Importação e exportação

Financeiro, orçamentos e materiais aceitam importação CSV.

- Use UTF-8.
- Inclua cabeçalho na primeira linha.
- Siga o formato apresentado na tela de importação.
- Revise as linhas rejeitadas no resultado.
- Não importe dados reais em ambiente de desenvolvimento sem autorização.

As exportações disponíveis incluem CSV e PDF conforme o módulo. Arquivos CSV possuem proteção contra fórmula maliciosa.

## 12. Boas práticas

- Sempre associe oportunidade, orçamento, obra e transação ao cliente correto.
- Use o próximo contato para não perder negociações.
- Registre ocorrências no dia em que forem identificadas.
- Informe motivo ao perder uma oportunidade ou cancelar um processo.
- Não compartilhe usuários ou senhas.
- Revise permissões periodicamente.
- Faça backup antes de operações de manutenção.
- Não use `DJANGO_DEBUG=True` em produção.

## 13. Problemas comuns

### Menu ou botão não aparece

Verifique se o usuário possui a permissão `view_*`, `add_*`, `change_*` ou `delete_*` necessária no grupo correto.

### Acesso retorna 403

O usuário está autenticado, mas não possui a permissão exigida pela ação. Solicite ao administrador a atribuição mínima necessária.

### Foto não é aceita

Confirme a extensão JPG, JPEG, PNG ou WEBP e o limite de 5 MB.

### Pagamento é rejeitado

Confira se o valor é maior que zero e não ultrapassa o saldo aberto da transação.

### Importação apresenta erros

Revise o cabeçalho, o formato das datas, os valores numéricos e os relacionamentos exigidos, como cliente existente em orçamentos.

## 14. Manutenção deste manual

Este arquivo faz parte da entrega do sistema e deve ser atualizado no mesmo pull request de qualquer mudança funcional ou de UX/UI.

### Mudança funcional

Atualize as seções afetadas quando houver:

- Nova tela, rota, campo, status ou permissão.
- Mudança de fluxo, cálculo, validação ou regra de negócio.
- Nova importação, exportação, relatório ou integração.
- Alteração de modelo ou relacionamento.

Registre também migração, testes e diagrama quando aplicável.

### Mudança de UI/UX

Atualize o manual quando houver:

- Renomeação ou movimentação de menu, botão ou campo.
- Mudança de layout, ordem das etapas ou fluxo de navegação.
- Inclusão de filtro, feedback, estado vazio ou mensagem de erro.
- Mudança no comportamento mobile, acessibilidade ou interação em campo.

Descreva o caminho que o usuário deve seguir, usando os nomes visíveis na interface atual.

### Checklist obrigatório para cada atualização

- [ ] Manual atualizado.
- [ ] Screenshots ou exemplos revisados, quando existirem.
- [ ] Testes funcionais atualizados.
- [ ] Teste mobile/acessibilidade atualizado para mudanças visuais.
- [ ] Diagrama atualizado se houver mudança de domínio ou infraestrutura.
- [ ] Data e versão do manual revisadas.

## 15. Referências

- [Roadmap do produto](ROADMAP.md)
- [Diagrama de dados](DIAGRAMA.md)
- [Controles de segurança e compliance](COMPLIANCE.md)
- [README do projeto](../README.md)
