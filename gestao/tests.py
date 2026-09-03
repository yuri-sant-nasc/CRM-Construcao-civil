from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.utils import timezone

from .models import (
    Cliente,
    AuditLog,
    DiarioObra,
    Falta,
    FotoObra,
    Funcionario,
    Item,
    ItemOrcamento,
    Orcamento,
    Oportunidade,
    Obra,
    Ocorrencia,
    Ponto,
    Transacao,
    VersaoOrcamento,
)
from .forms import ObraForm, OportunidadeForm, FotoObraForm
from .importers import import_csv


class WpnModelTests(TestCase):
    def test_funcionario_can_be_created(self):
        funcionario = Funcionario.objects.create(
            nome_completo='Maria Souza',
            funcao='Pedreira',
            estado_civil='Solteira',
            data_admissao=date(2024, 1, 10),
            data_nascimento=date(1990, 5, 15),
            cpf='12345678901',
            bairro='Centro',
            rua='Rua das Flores',
            numero='42',
            cidade='Tatuí',
            estado='SP',
            celular='(15) 99999-1234',
            email='maria@wpp.com',
        )

        self.assertEqual(str(funcionario), 'Maria Souza')
        self.assertTrue(funcionario.ativo)

    def test_cliente_can_be_created(self):
        cliente = Cliente.objects.create(
            nome_completo='João da Silva',
            empresa='Construtora Alpha',
            cargo='Diretor',
            cnpj='12345678000199',
            contato_anterior=date(2024, 2, 1),
            descricao_pedido='Ampliação da obra',
            bairro='Jardim Paulista',
            rua='Av. Atlântica',
            numero='100',
            cidade='Tatuí',
            estado='SP',
            telefone='(15) 3333-4444',
            email='contato@alpha.com',
        )

        self.assertEqual(str(cliente), 'João da Silva')
        self.assertTrue(cliente.ativo)

    def test_falta_and_budget_and_transaction_and_item_can_be_created(self):
        funcionario = Funcionario.objects.create(
            nome_completo='José Lima',
            funcao='Mestre de Obra',
            estado_civil='Casado',
            data_admissao=date(2023, 6, 1),
            data_nascimento=date(1985, 9, 12),
            cpf='10987654321',
            bairro='Centro',
            rua='Av. Brasil',
            numero='20',
            cidade='Tatuí',
            estado='SP',
            celular='(15) 98888-7777',
            email='jose@wpn.com',
        )
        cliente = Cliente.objects.create(
            nome_completo='Ana Pereira',
            empresa='Pereira Ltda',
            cargo='Gerente',
            cnpj='98765432000188',
            contato_anterior=date(2024, 3, 10),
            descricao_pedido='Casa térrea',
            bairro='Parque',
            rua='Rua da Paz',
            numero='77',
            cidade='Tatuí',
            estado='SP',
            telefone='(15) 4000-5000',
            email='ana@pereira.com',
        )

        falta = Falta.objects.create(
            funcionario=funcionario,
            data=date(2024, 4, 8),
            presente=False,
            motivo='Doença',
            status='justificada',
        )
        transacao = Transacao.objects.create(
            valor='1500.00',
            data=date(2024, 4, 9),
            descricao='Pagamento de salário',
            tipo='saida',
            categoria='salarios',
        )
        orcamento = Orcamento.objects.create(
            cliente=cliente,
            data_orcamento=date(2024, 4, 9),
            descricao='Orçamento de reforma',
            valor='5400.00',
        )
        item = Item.objects.create(
            nome='Cimento CP II',
            descricao='Saco de cimento',
            quantidade_disponivel=120,
            fabricante='MPC',
            data_aquisicao=date(2024, 4, 1),
            data_vencimento=date(2025, 4, 1),
        )

        self.assertEqual(falta.status, 'justificada')
        self.assertEqual(str(transacao), 'Pagamento de salário')
        self.assertEqual(str(orcamento), 'Orçamento de reforma')
        self.assertEqual(str(item), 'Cimento CP II')

    def test_employee_can_register_point_and_user_login(self):
        user = get_user_model().objects.create_user(username='joao', password='senha123')
        funcionario = Funcionario.objects.create(
            usuario=user,
            nome_completo='João da Silva',
            funcao='Pedreiro',
            estado_civil='Solteiro',
            data_admissao=date(2024, 1, 1),
            data_nascimento=date(1994, 3, 5),
            cpf='22233344455',
            bairro='Centro',
            rua='Rua A',
            numero='15',
            cidade='Tatuí',
            estado='SP',
            celular='(15) 99888-1122',
            email='joao@wpn.com',
        )

        ponto = Ponto.objects.create(
            funcionario=funcionario,
            data=date(2024, 5, 10),
            entrada=timezone.make_aware(datetime(2024, 5, 10, 7, 0)),
            saida=timezone.make_aware(datetime(2024, 5, 10, 17, 30)),
        )

        self.assertEqual(str(ponto), 'João da Silva - 2024-05-10')
        self.assertTrue(user.is_authenticated)

    def test_csv_import_creates_finance_transaction_and_reports_invalid_rows(self):
        csv_file = SimpleUploadedFile(
            'financeiro.csv',
            b'valor,data,descricao,tipo,categoria\n'
            b'1250,2026-08-21,Compra de material,saida,materiais\n'
            b'invalido,2026-08-21,Linha incorreta,entrada,outros\n',
            content_type='text/csv',
        )

        imported, errors = import_csv(csv_file, 'financeiro')

        self.assertEqual(imported, 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(Transacao.objects.count(), 1)

    def test_csv_import_requires_existing_client_for_budget(self):
        csv_file = SimpleUploadedFile(
            'orcamentos.csv',
            b'cliente,data_orcamento,descricao,valor\n'
            b'Cliente inexistente,2026-08-21,Reforma,5400.00\n',
            content_type='text/csv',
        )

        imported, errors = import_csv(csv_file, 'orcamento')

        self.assertEqual(imported, 0)
        self.assertIn('cliente não encontrado', errors[0])

    def test_obra_can_group_budget_and_transaction(self):
        cliente = Cliente.objects.create(
            nome_completo='Cliente da Obra', empresa='Empresa', cargo='Diretor',
            cnpj='11122233000144', descricao_pedido='Reforma', bairro='Centro',
            rua='Rua A', numero='1', cidade='Tatuí', estado='SP',
            telefone='15999999999', email='obra@example.com',
        )
        obra = Obra.objects.create(
            nome='Residência Central', cliente=cliente, endereco='Rua A, 1',
            data_inicio=date(2026, 8, 21),
        )
        transaction = Transacao.objects.create(
            valor='200.00', data=date(2026, 8, 21), descricao='Material',
            tipo='saida', categoria='materiais', obra=obra,
        )

        self.assertEqual(transaction.obra, obra)

    def test_audit_log_records_authenticated_post(self):
        user = get_user_model().objects.create_user(username='auditor', password='senha123')
        client = Client()
        client.force_login(user)
        response = client.post('/logout/', secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(AuditLog.objects.filter(user=user, path='/logout/', action='POST').exists())


class SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='viewer', password='senha123')
        self.client.force_login(self.user)

    def test_authenticated_user_without_permission_is_forbidden(self):
        response = self.client.get('/clientes/')

        self.assertEqual(response.status_code, 403)

    def test_user_with_view_permission_can_access_clientes(self):
        permission = Permission.objects.get(codename='view_cliente')
        self.user.user_permissions.add(permission)

        response = self.client.get('/clientes/')

        self.assertEqual(response.status_code, 200)

    def test_import_requires_permission_for_selected_resource(self):
        permission = Permission.objects.get(codename='add_item')
        self.user.user_permissions.add(permission)

        response = self.client.get('/materiais/importar/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/financeiro/importar/').status_code, 403)

    def test_opportunity_list_can_be_filtered_by_stage(self):
        permission = Permission.objects.get(codename='view_oportunidade')
        self.user.user_permissions.add(permission)
        cliente = Cliente.objects.create(
            nome_completo='Cliente Comercial', empresa='Construtora Beta', cargo='Diretor',
            cnpj='55566677000188', descricao_pedido='Reforma', bairro='Centro',
            rua='Rua B', numero='2', cidade='Tatuí', estado='SP',
            telefone='15988887777', email='comercial@beta.com',
        )
        Oportunidade.objects.create(cliente=cliente, titulo='Reforma aprovada', etapa='aprovado')
        Oportunidade.objects.create(cliente=cliente, titulo='Nova prospecção', etapa='novo')

        response = self.client.get('/oportunidades/?etapa=aprovado')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reforma aprovada')
        self.assertNotContains(response, 'Nova prospecção')

    def test_opportunity_edit_requires_change_permission(self):
        cliente = Cliente.objects.create(
            nome_completo='Cliente Comercial', empresa='Construtora Beta', cargo='Diretor',
            cnpj='55566677000188', descricao_pedido='Reforma', bairro='Centro',
            rua='Rua B', numero='2', cidade='Tatuí', estado='SP',
            telefone='15988887777', email='comercial@beta.com',
        )
        oportunidade = Oportunidade.objects.create(cliente=cliente, titulo='Negociação')

        response = self.client.get(f'/oportunidades/{oportunidade.pk}/editar/')

        self.assertEqual(response.status_code, 403)

    def test_lost_opportunity_requires_reason(self):
        form = OportunidadeForm(data={
            'cliente': '', 'titulo': 'Obra perdida', 'etapa': 'perdido',
            'origem': 'outro', 'probabilidade_fechamento': 0,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('motivo_perda', form.errors)

    def test_opportunity_probability_cannot_exceed_one_hundred(self):
        form = OportunidadeForm(data={
            'cliente': '', 'titulo': 'Probabilidade inválida', 'etapa': 'novo',
            'origem': 'outro', 'probabilidade_fechamento': 101,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('probabilidade_fechamento', form.errors)

    def test_stage_history_is_recorded_only_when_stage_changes(self):
        change_permission = Permission.objects.get(codename='change_oportunidade')
        self.user.user_permissions.add(change_permission)
        cliente = Cliente.objects.create(
            nome_completo='Cliente Histórico', empresa='Empresa', cargo='Diretor',
            cnpj='77788899000166', descricao_pedido='Reforma', bairro='Centro',
            rua='Rua C', numero='3', cidade='Tatuí', estado='SP',
            telefone='15977776666', email='historico@example.com',
        )
        oportunidade = Oportunidade.objects.create(cliente=cliente, titulo='Reforma', etapa='novo')

        response = self.client.post(f'/oportunidades/{oportunidade.pk}/editar/', {
            'cliente': cliente.pk, 'titulo': 'Reforma atualizada', 'etapa': 'visita',
            'origem': 'site', 'probabilidade_fechamento': 20,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/oportunidades/')
        oportunidade.refresh_from_db()
        self.assertEqual(oportunidade.historico.count(), 1)
        self.client.post(f'/oportunidades/{oportunidade.pk}/editar/', {
            'cliente': cliente.pk, 'titulo': 'Reforma atualizada', 'etapa': 'visita',
            'origem': 'site', 'probabilidade_fechamento': 20,
        })

        oportunidade.refresh_from_db()
        self.assertEqual(oportunidade.etapa, 'visita')
        self.assertEqual(oportunidade.historico.count(), 1)
        historico = oportunidade.historico.get()
        self.assertEqual(historico.etapa_anterior, 'novo')
        self.assertEqual(historico.etapa_nova, 'visita')

    def test_approved_opportunity_converts_to_one_budget(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename='change_oportunidade'),
            Permission.objects.get(codename='add_orcamento'),
        )
        cliente = Cliente.objects.create(
            nome_completo='Cliente Conversão', empresa='Empresa', cargo='Diretor',
            cnpj='88899900000155', descricao_pedido='Ampliação', bairro='Centro',
            rua='Rua D', numero='4', cidade='Tatuí', estado='SP',
            telefone='15966665555', email='conversao@example.com',
        )
        oportunidade = Oportunidade.objects.create(
            cliente=cliente, titulo='Ampliação aprovada', etapa='aprovado', valor_estimado='25000.00',
        )

        first = self.client.post(f'/oportunidades/{oportunidade.pk}/converter-orcamento/')
        second = self.client.post(f'/oportunidades/{oportunidade.pk}/converter-orcamento/')

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Orcamento.objects.filter(oportunidade=oportunidade).count(), 1)
        self.assertEqual(Orcamento.objects.get(oportunidade=oportunidade).valor, 25000)

    def test_opportunity_conversion_requires_budget_permission(self):
        cliente = Cliente.objects.create(
            nome_completo='Cliente Sem Permissão', empresa='Empresa', cargo='Diretor',
            cnpj='99900011000144', descricao_pedido='Reforma', bairro='Centro',
            rua='Rua E', numero='5', cidade='Tatuí', estado='SP',
            telefone='15955554444', email='sem-permissao@example.com',
        )
        oportunidade = Oportunidade.objects.create(cliente=cliente, titulo='Reforma aprovada', etapa='aprovado')
        self.user.user_permissions.add(Permission.objects.get(codename='change_oportunidade'))

        response = self.client.post(f'/oportunidades/{oportunidade.pk}/converter-orcamento/')

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Orcamento.objects.filter(oportunidade=oportunidade).exists())

    def test_work_form_rejects_progress_above_one_hundred(self):
        form = ObraForm(data={'nome': 'Obra inválida', 'percentual_concluido': 101})

        self.assertFalse(form.is_valid())
        self.assertIn('percentual_concluido', form.errors)

    def test_completed_work_requires_full_progress(self):
        cliente = Cliente.objects.create(
            nome_completo='Cliente Status', empresa='Empresa', cargo='Diretor',
            cnpj='33344455000122', descricao_pedido='Construção', bairro='Centro',
            rua='Rua I', numero='9', cidade='Tatuí', estado='SP',
            telefone='15933330000', email='status@example.com',
        )
        obra = Obra(nome='Obra incompleta', cliente=cliente, endereco='Rua I, 9', data_inicio=date(2026, 1, 1), status='concluida', percentual_concluido=80)

        with self.assertRaises(ValidationError):
            obra.full_clean()

    def test_work_list_filters_by_status(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_obra'))
        cliente = Cliente.objects.create(
            nome_completo='Cliente Filtro', empresa='Empresa', cargo='Diretor',
            cnpj='66677788000111', descricao_pedido='Construção', bairro='Centro',
            rua='Rua J', numero='10', cidade='Tatuí', estado='SP',
            telefone='15966660000', email='filtro@example.com',
        )
        Obra.objects.create(nome='Obra em andamento', cliente=cliente, endereco='Rua J, 10', data_inicio=date(2026, 1, 1), status='andamento')
        Obra.objects.create(nome='Obra planejada', cliente=cliente, endereco='Rua J, 10', data_inicio=date(2026, 2, 1), status='planejamento')

        response = self.client.get('/obras/?status=andamento')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Obra em andamento')
        self.assertNotContains(response, 'Obra planejada')

    def test_work_team_diary_and_occurrence_are_related(self):
        cliente = Cliente.objects.create(
            nome_completo='Cliente Obra', empresa='Empresa', cargo='Diretor',
            cnpj='44455566000133', descricao_pedido='Construção', bairro='Centro',
            rua='Rua F', numero='6', cidade='Tatuí', estado='SP',
            telefone='15944443333', email='obra-operacional@example.com',
        )
        funcionario = Funcionario.objects.create(
            nome_completo='Responsável da Obra', funcao='Engenheiro', estado_civil='Casado',
            data_admissao=date(2025, 1, 1), data_nascimento=date(1980, 1, 1),
            cpf='33344455566', bairro='Centro', rua='Rua F', numero='6', cidade='Tatuí',
            estado='SP', celular='15933332222', email='engenheiro@example.com',
        )
        obra = Obra.objects.create(nome='Obra Operacional', cliente=cliente, responsavel=funcionario, percentual_concluido=35, endereco='Rua F, 6', data_inicio=date(2026, 1, 1))
        obra.equipe.add(funcionario)
        diario = DiarioObra.objects.create(obra=obra, autor=self.user, resumo='Fundação concluída.')
        ocorrencia = Ocorrencia.objects.create(obra=obra, autor=self.user, titulo='Atraso de material', descricao='Entrega reagendada.')

        self.assertEqual(obra.equipe.count(), 1)
        self.assertEqual(diario.obra, obra)
        self.assertEqual(ocorrencia.status, 'aberta')

    def test_photo_form_rejects_invalid_extension_and_large_file(self):
        cliente = Cliente.objects.create(
            nome_completo='Cliente Foto', empresa='Empresa', cargo='Diretor',
            cnpj='22233344000177', descricao_pedido='Construção', bairro='Centro',
            rua='Rua G', numero='7', cidade='Tatuí', estado='SP',
            telefone='15922221111', email='foto@example.com',
        )
        obra = Obra.objects.create(nome='Obra Foto', cliente=cliente, endereco='Rua G, 7', data_inicio=date(2026, 1, 1))
        invalid = SimpleUploadedFile('nota.txt', b'texto', content_type='text/plain')
        large = SimpleUploadedFile('foto.jpg', b'x' * (5 * 1024 * 1024 + 1), content_type='image/jpeg')

        invalid_form = FotoObraForm(data={'obra': obra.pk}, files={'arquivo': invalid})
        large_form = FotoObraForm(data={'obra': obra.pk}, files={'arquivo': large})

        self.assertFalse(invalid_form.is_valid())
        self.assertFalse(large_form.is_valid())

    def test_budget_items_calculate_margin_and_pdf(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_orcamento'),
            Permission.objects.get(codename='add_itemorcamento'),
        )
        cliente = Cliente.objects.create(
            nome_completo='Cliente Orçamento', empresa='Empresa', cargo='Diretor',
            cnpj='12131415000199', descricao_pedido='Construção', bairro='Centro',
            rua='Rua K', numero='11', cidade='Tatuí', estado='SP',
            telefone='15912220000', email='orcamento@example.com',
        )
        orcamento = Orcamento.objects.create(cliente=cliente, data_orcamento=date(2026, 1, 1), descricao='Casa térrea', valor='1500.00')

        detail = self.client.post(f'/orcamentos/{orcamento.pk}/', {
            'categoria': 'material', 'descricao': 'Cimento', 'quantidade': '10',
            'custo_unitario': '100', 'margem_percentual': '20',
        })
        pdf = self.client.get(f'/orcamentos/{orcamento.pk}/proposta.pdf')

        self.assertEqual(detail.status_code, 302)
        item = ItemOrcamento.objects.get(orcamento=orcamento)
        self.assertEqual(item.total, 1200)
        self.assertEqual(orcamento.total_composicao, 1200)
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf['Content-Type'], 'application/pdf')

    def test_budget_adjustment_creates_version_with_item_snapshot(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_orcamento'),
            Permission.objects.get(codename='change_orcamento'),
        )
        cliente = Cliente.objects.create(
            nome_completo='Cliente Reajuste', empresa='Empresa', cargo='Diretor',
            cnpj='16171819000188', descricao_pedido='Construção', bairro='Centro',
            rua='Rua L', numero='12', cidade='Tatuí', estado='SP',
            telefone='15916660000', email='reajuste@example.com',
        )
        orcamento = Orcamento.objects.create(cliente=cliente, data_orcamento=date(2026, 1, 1), descricao='Reforma', valor='1000.00')
        ItemOrcamento.objects.create(orcamento=orcamento, categoria='servico', descricao='Projeto', quantidade='1', custo_unitario='500', margem_percentual='10')

        response = self.client.post(f'/orcamentos/{orcamento.pk}/', {'action': 'reajuste', 'percentual': '10', 'motivo': 'Atualização de preços'})

        self.assertEqual(response.status_code, 302)
        orcamento.refresh_from_db()
        versao = VersaoOrcamento.objects.get(orcamento=orcamento)
        self.assertEqual(orcamento.valor, 1100)
        self.assertEqual(versao.numero, 1)
        self.assertEqual(versao.valor_anterior, 1000)
        self.assertEqual(versao.valor_novo, 1100)
        self.assertEqual(versao.itens_snapshot[0]['descricao'], 'Projeto')

    def test_work_operation_page_registers_and_downloads_records(self):
        permissions = Permission.objects.filter(codename__in=(
            'view_obra', 'add_diarioobra', 'add_ocorrencia', 'add_fotoobra', 'view_fotoobra',
        ))
        self.user.user_permissions.add(*permissions)
        cliente = Cliente.objects.create(
            nome_completo='Cliente Operação', empresa='Empresa', cargo='Diretor',
            cnpj='11122233000199', descricao_pedido='Construção', bairro='Centro',
            rua='Rua H', numero='8', cidade='Tatuí', estado='SP',
            telefone='15911110000', email='operacao@example.com',
        )
        obra = Obra.objects.create(nome='Obra em Operação', cliente=cliente, endereco='Rua H, 8', data_inicio=date(2026, 1, 1))

        page = self.client.get(f'/obras/{obra.pk}/operacao/')
        diario = self.client.post(f'/obras/{obra.pk}/operacao/', {
            'action': 'diario', 'diario-obra': obra.pk, 'diario-data': '2026-09-02',
            'diario-resumo': 'Concretagem realizada.',
        })
        ocorrencia = self.client.post(f'/obras/{obra.pk}/operacao/', {
            'action': 'ocorrencia', 'ocorrencia-obra': obra.pk,
            'ocorrencia-titulo': 'Chuva', 'ocorrencia-descricao': 'Serviço interrompido.',
            'ocorrencia-status': 'aberta',
        })
        foto_file = SimpleUploadedFile('frente.jpg', b'foto', content_type='image/jpeg')
        foto = self.client.post(f'/obras/{obra.pk}/operacao/', {
            'action': 'foto', 'foto-obra': obra.pk, 'foto-legenda': 'Frente da obra',
            'foto-arquivo': foto_file,
        })

        self.assertEqual(page.status_code, 200)
        self.assertEqual(diario.status_code, 302)
        self.assertEqual(ocorrencia.status_code, 302)
        self.assertEqual(foto.status_code, 302)
        arquivo = FotoObra.objects.get(obra=obra)
        self.assertEqual(self.client.get(f'/fotos-obras/{arquivo.pk}/download/').status_code, 200)
