from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.utils import timezone

from .models import (
    Cliente,
    AuditLog,
    Falta,
    Funcionario,
    Item,
    Orcamento,
    Obra,
    Ponto,
    Transacao,
)
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
