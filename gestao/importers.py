import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Cliente, Item, Orcamento, Transacao


IMPORT_CONFIG = {
    'financeiro': {
        'title': 'Importar financeiro',
        'description': 'Colunas: valor, data, descricao, tipo, categoria',
        'fields': ['valor', 'data', 'descricao', 'tipo', 'categoria'],
        'example': '1500,2026-08-21,Pagamento de fornecedor,saida,materiais',
    },
    'orcamento': {
        'title': 'Importar orçamentos',
        'description': 'Colunas: cliente, data_orcamento, descricao, valor. O cliente deve existir pelo nome ou e-mail.',
        'fields': ['cliente', 'data_orcamento', 'descricao', 'valor'],
        'example': 'Cliente Exemplo,2026-08-21,Reforma residencial,5400.00',
    },
    'material': {
        'title': 'Importar materiais',
        'description': 'Colunas: nome, descricao, quantidade_disponivel, tipo, fabricante, data_aquisicao, data_vencimento',
        'fields': ['nome', 'descricao', 'quantidade_disponivel', 'tipo', 'fabricante', 'data_aquisicao', 'data_vencimento'],
        'example': 'Cimento CP II,Saco de cimento,120,material,MPC,2026-08-01,2027-08-01',
    },
}


def _clean(value):
    return (value or '').strip()


def _parse_date(value, field, required=True):
    value = _clean(value)
    if not value and not required:
        return None
    if not value:
        raise ValueError(f'{field} é obrigatório.')
    for date_format in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue
    raise ValueError(f'{field} deve estar em AAAA-MM-DD ou DD/MM/AAAA.')


def _parse_decimal(value):
    value = _clean(value).replace('R$', '').replace(' ', '')
    if ',' in value and '.' in value:
        value = value.replace('.', '').replace(',', '.')
    else:
        value = value.replace(',', '.')
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError('valor deve ser numérico.') from exc


def _reader(upload):
    try:
        content = upload.read().decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('o arquivo deve estar salvo em UTF-8.') from exc
    sample = content[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;')
    except csv.Error:
        dialect = csv.excel
    return csv.DictReader(io.StringIO(content), dialect=dialect)


def _validate_headers(reader, fields):
    headers = [(_clean(header)).lower() for header in (reader.fieldnames or [])]
    missing = [field for field in fields if field not in headers]
    if missing:
        raise ValueError(f'colunas obrigatórias ausentes: {", ".join(missing)}.')
    reader.fieldnames = headers


def _find_client(value):
    value = _clean(value)
    client = Cliente.objects.filter(nome_completo__iexact=value).first()
    if client is None:
        client = Cliente.objects.filter(email__iexact=value).first()
    if client is None:
        raise ValueError(f'cliente não encontrado: {value}.')
    return client


def _build_object(kind, row):
    if kind == 'financeiro':
        tipo = _clean(row['tipo']).lower()
        categoria = _clean(row['categoria']).lower()
        if tipo not in dict(Transacao.TIPO_CHOICES):
            raise ValueError('tipo deve ser entrada ou saida.')
        if categoria not in dict(Transacao.CATEGORIA_CHOICES):
            raise ValueError('categoria inválida.')
        return Transacao(
            valor=_parse_decimal(row['valor']),
            data=_parse_date(row['data'], 'data'),
            descricao=_clean(row['descricao']),
            tipo=tipo,
            categoria=categoria,
        )
    if kind == 'orcamento':
        return Orcamento(
            cliente=_find_client(row['cliente']),
            data_orcamento=_parse_date(row['data_orcamento'], 'data_orcamento'),
            descricao=_clean(row['descricao']),
            valor=_parse_decimal(row['valor']),
        )
    if kind == 'material':
        tipo = _clean(row['tipo']).lower() or 'material'
        if tipo not in dict(Item.TIPO_CHOICES):
            raise ValueError('tipo deve ser material, ferramenta ou epi.')
        return Item(
            nome=_clean(row['nome']),
            descricao=_clean(row['descricao']),
            quantidade_disponivel=int(_clean(row['quantidade_disponivel'])),
            tipo=tipo,
            fabricante=_clean(row['fabricante']),
            data_aquisicao=_parse_date(row['data_aquisicao'], 'data_aquisicao'),
            data_vencimento=_parse_date(row['data_vencimento'], 'data_vencimento', required=False),
        )
    raise ValueError('tipo de importação inválido.')


def import_csv(upload, kind):
    if kind not in IMPORT_CONFIG:
        raise ValueError('tipo de importação inválido.')
    reader = _reader(upload)
    _validate_headers(reader, IMPORT_CONFIG[kind]['fields'])
    imported = 0
    errors = []
    for line_number, row in enumerate(reader, start=2):
        try:
            if not any(_clean(value) for value in row.values() if value is not None):
                continue
            with transaction.atomic():
                obj = _build_object(kind, row)
                obj.full_clean()
                obj.save()
            imported += 1
        except (TypeError, ValueError, InvalidOperation, OverflowError, ValidationError) as exc:
            errors.append(f'linha {line_number}: {exc}')
    return imported, errors
