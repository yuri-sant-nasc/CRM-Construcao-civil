from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db.models import F, Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.utils.dateparse import parse_date

from .exports import export_csv
from .forms import (
    ClienteForm,
    DiarioObraForm,
    FaltaForm,
    FotoObraForm,
    FuncionarioForm,
    ItemForm,
    LoginForm,
    ImportacaoCSVForm,
    ItemOrcamentoForm,
    ReajusteOrcamentoForm,
    ObraForm,
    OportunidadeForm,
    OcorrenciaForm,
    OrcamentoForm,
    PontoForm,
    TransacaoForm,
)
from .models import Cliente, Falta, FotoObra, Funcionario, HistoricoOportunidade, Item, ItemOrcamento, Obra, Oportunidade, Orcamento, Ponto, Transacao, VersaoOrcamento
from .importers import IMPORT_CONFIG, import_csv
from .pdf_utils import build_pdf_response


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Simple brute-force protection
            cache_key = f'login_attempts_{username}'
            attempts = cache.get(cache_key, 0)
            if attempts >= 5:
                messages.error(request, 'Muitas tentativas falhas. Tente novamente mais tarde.')
                return render(request, 'gestao/login.html', {'form': form})
                
            user = authenticate(username=username, password=password)
            if user is not None:
                cache.delete(cache_key)
                login(request, user)
                messages.success(request, 'Login realizado com sucesso.')
                return redirect('dashboard')
                
            cache.set(cache_key, attempts + 1, 300) # Block for 5 minutes after 5 fails
            messages.error(request, 'Credenciais inválidas.')
    else:
        form = LoginForm()
    return render(request, 'gestao/login.html', {'form': form})


@login_required(login_url='login')
@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@permission_required('gestao.view_transacao', raise_exception=True)
def dashboard(request):
    funcionarios = Funcionario.objects.filter(ativo=True).count()
    clientes = Cliente.objects.filter(ativo=True).count()
    faltas = Falta.objects.filter(ativo=True).count()
    orcamentos = Orcamento.objects.count()
    transacoes = Transacao.objects.all()
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if data_inicio:
        parsed_inicio = parse_date(data_inicio)
        if parsed_inicio:
            transacoes = transacoes.filter(data__gte=parsed_inicio)
    if data_fim:
        parsed_fim = parse_date(data_fim)
        if parsed_fim:
            transacoes = transacoes.filter(data__lte=parsed_fim)
            
    receitas = transacoes.filter(tipo='entrada').aggregate(total=Sum('valor'))['total'] or 0
    despesas = transacoes.filter(tipo='saida').aggregate(total=Sum('valor'))['total'] or 0
    saldo = receitas - despesas
    itens = Item.objects.count()
    pontos = Ponto.objects.count()
    estoque_baixo = Item.objects.filter(quantidade_disponivel__lte=F('quantidade_minima')).order_by('quantidade_disponivel')[:5]

    recent_funcionarios = Funcionario.objects.filter(ativo=True).order_by('-id')[:5]
    recent_clientes = Cliente.objects.filter(ativo=True).order_by('-id')[:5]
    recent_orcamentos = Orcamento.objects.select_related('cliente').order_by('-data_orcamento')[:5]
    recent_transacoes = Transacao.objects.order_by('-data')[:5]

    monthly_flow = []
    monthly_totals = []
    for month in range(6):
        current_date = timezone.now().replace(day=1)
        month_date = current_date.month - month
        year = current_date.year
        while month_date <= 0:
            month_date += 12
            year -= 1
        while month_date > 12:
            month_date -= 12
            year += 1
        total_entrada = Transacao.objects.filter(data__year=year, data__month=month_date, tipo='entrada').aggregate(total=Sum('valor'))['total'] or 0
        total_saida = Transacao.objects.filter(data__year=year, data__month=month_date, tipo='saida').aggregate(total=Sum('valor'))['total'] or 0
        monthly_flow.append({
            'label': f'{year}-{month_date:02d}',
            'entrada': float(total_entrada),
            'saida': float(total_saida),
            'saldo': float(total_entrada - total_saida),
        })
    monthly_flow.reverse()
    chart_max = max((max(item['entrada'], item['saida']) for item in monthly_flow), default=0) or 1
    for item in monthly_flow:
        item['entrada_percent'] = max(6, round(item['entrada'] / chart_max * 100)) if item['entrada'] else 0
        item['saida_percent'] = max(6, round(item['saida'] / chart_max * 100)) if item['saida'] else 0

    context = {
        'funcionarios': funcionarios,
        'clientes': clientes,
        'faltas': faltas,
        'orcamentos': orcamentos,
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
        'itens': itens,
        'pontos': pontos,
        'estoque_baixo': estoque_baixo,
        'data_inicio': data_inicio or '',
        'data_fim': data_fim or '',
        'recent_funcionarios': recent_funcionarios,
        'recent_clientes': recent_clientes,
        'recent_orcamentos': recent_orcamentos,
        'recent_transacoes': recent_transacoes,
        'monthly_flow': monthly_flow,
        'chart_max': chart_max,
    }
    return render(request, 'gestao/dashboard.html', context)


@login_required(login_url='login')
@permission_required('gestao.view_funcionario', raise_exception=True)
def funcionarios(request):
    registros = Funcionario.objects.filter(ativo=True).order_by('-id')
    return render(request, 'gestao/lista.html', {'titulo': 'Funcionários', 'registros': registros, 'tipo': 'funcionario'})


@login_required(login_url='login')
@permission_required('gestao.add_funcionario', raise_exception=True)
def funcionario_create(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('funcionarios')
    else:
        form = FuncionarioForm()
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Novo Funcionário'})


@login_required(login_url='login')
@permission_required('gestao.change_funcionario', raise_exception=True)
def funcionario_update(request, pk):
    obj = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('funcionarios')
    else:
        form = FuncionarioForm(instance=obj)
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Funcionário'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_funcionario', raise_exception=True)
def funcionario_delete(request, pk):
    obj = get_object_or_404(Funcionario, pk=pk)
    obj.ativo = False
    obj.save()
    return redirect('funcionarios')


@login_required(login_url='login')
@permission_required('gestao.view_cliente', raise_exception=True)
def clientes(request):
    registros = Cliente.objects.filter(ativo=True).order_by('-id')
    return render(request, 'gestao/lista.html', {'titulo': 'Clientes', 'registros': registros, 'tipo': 'cliente'})


@login_required(login_url='login')
@permission_required('gestao.view_obra', raise_exception=True)
def obras(request):
    registros = Obra.objects.select_related('cliente').all()
    status = request.GET.get('status')
    responsavel = request.GET.get('responsavel')
    if status in dict(Obra.STATUS_CHOICES):
        registros = registros.filter(status=status)
    if responsavel and responsavel.isdigit():
        registros = registros.filter(responsavel_id=responsavel)
    return render(request, 'gestao/lista.html', {
        'titulo': 'Obras', 'registros': registros, 'tipo': 'obra',
        'status_obra_choices': Obra.STATUS_CHOICES,
        'status_obra_atual': status or '',
        'responsaveis_obra': Funcionario.objects.filter(ativo=True).order_by('nome_completo'),
        'responsavel_obra_atual': responsavel or '',
    })


@login_required(login_url='login')
@permission_required('gestao.add_obra', raise_exception=True)
def obra_create(request):
    form = ObraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('obras')
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Nova Obra'})


@login_required(login_url='login')
@permission_required('gestao.change_obra', raise_exception=True)
def obra_update(request, pk):
    obj = get_object_or_404(Obra, pk=pk)
    form = ObraForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('obras')
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Obra'})


@login_required(login_url='login')
@permission_required('gestao.view_obra', raise_exception=True)
def obra_operacao(request, pk):
    obra = get_object_or_404(Obra.objects.select_related('cliente', 'responsavel'), pk=pk)
    diario_form = DiarioObraForm(prefix='diario')
    ocorrencia_form = OcorrenciaForm(prefix='ocorrencia')
    foto_form = FotoObraForm(prefix='foto')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'diario':
            diario_form = DiarioObraForm(request.POST, prefix='diario')
            if diario_form.is_valid() and diario_form.cleaned_data['obra'] == obra:
                diario = diario_form.save(commit=False)
                diario.autor = request.user
                diario.save()
                messages.success(request, 'Diário de obra registrado.')
                return redirect('obra_operacao', pk=obra.pk)
        elif action == 'ocorrencia':
            ocorrencia_form = OcorrenciaForm(request.POST, prefix='ocorrencia')
            if ocorrencia_form.is_valid() and ocorrencia_form.cleaned_data['obra'] == obra:
                ocorrencia = ocorrencia_form.save(commit=False)
                ocorrencia.autor = request.user
                ocorrencia.save()
                messages.success(request, 'Ocorrência registrada.')
                return redirect('obra_operacao', pk=obra.pk)
        elif action == 'foto':
            foto_form = FotoObraForm(request.POST, request.FILES, prefix='foto')
            if foto_form.is_valid() and foto_form.cleaned_data['obra'] == obra:
                foto = foto_form.save(commit=False)
                foto.autor = request.user
                foto.save()
                messages.success(request, 'Foto enviada.')
                return redirect('obra_operacao', pk=obra.pk)
    return render(request, 'gestao/obra_operacao.html', {
        'obra': obra,
        'diarios': obra.diarios.select_related('autor').all(),
        'ocorrencias': obra.ocorrencias.select_related('autor').all(),
        'fotos': obra.fotos.select_related('autor').all(),
        'diario_form': diario_form,
        'ocorrencia_form': ocorrencia_form,
        'foto_form': foto_form,
    })


@login_required(login_url='login')
@permission_required('gestao.view_fotoobra', raise_exception=True)
def foto_obra_download(request, pk):
    foto = get_object_or_404(FotoObra, pk=pk)
    if not foto.arquivo:
        return redirect('obra_operacao', pk=foto.obra_id)
    return FileResponse(foto.arquivo.open('rb'), as_attachment=True, filename=foto.arquivo.name.rsplit('/', 1)[-1])


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_obra', raise_exception=True)
def obra_delete(request, pk):
    Obra.objects.filter(pk=pk).delete()
    return redirect('obras')


@login_required(login_url='login')
@permission_required('gestao.add_cliente', raise_exception=True)
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes')
    else:
        form = ClienteForm()
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Novo Cliente'})


@login_required(login_url='login')
@permission_required('gestao.change_cliente', raise_exception=True)
def cliente_update(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('clientes')
    else:
        form = ClienteForm(instance=obj)
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Cliente'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_cliente', raise_exception=True)
def cliente_delete(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    obj.ativo = False
    obj.save()
    return redirect('clientes')


@login_required(login_url='login')
@permission_required('gestao.view_oportunidade', raise_exception=True)
def oportunidades(request):
    registros = Oportunidade.objects.select_related('cliente').order_by('-atualizado_em')
    etapa = request.GET.get('etapa')
    if etapa in dict(Oportunidade.ETAPA_CHOICES):
        registros = registros.filter(etapa=etapa)
    return render(request, 'gestao/lista.html', {
        'titulo': 'Oportunidades comerciais',
        'registros': registros,
        'tipo': 'oportunidade',
        'etapas_oportunidade': Oportunidade.ETAPA_CHOICES,
        'etapa_atual': etapa or '',
    })


@login_required(login_url='login')
@permission_required('gestao.add_oportunidade', raise_exception=True)
def oportunidade_create(request):
    form = OportunidadeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        oportunidade = form.save()
        HistoricoOportunidade.objects.create(oportunidade=oportunidade, etapa_nova=oportunidade.etapa, alterado_por=request.user)
        return redirect('oportunidades')
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Nova oportunidade'})


@login_required(login_url='login')
@permission_required('gestao.change_oportunidade', raise_exception=True)
def oportunidade_update(request, pk):
    obj = get_object_or_404(Oportunidade, pk=pk)
    etapa_anterior = obj.etapa
    form = OportunidadeForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        etapa_nova = form.cleaned_data['etapa']
        oportunidade = form.save()
        if etapa_anterior != etapa_nova:
            HistoricoOportunidade.objects.create(
                oportunidade=oportunidade,
                etapa_anterior=etapa_anterior,
                etapa_nova=etapa_nova,
                alterado_por=request.user,
            )
        return redirect('oportunidades')
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar oportunidade'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_oportunidade', raise_exception=True)
def oportunidade_delete(request, pk):
    Oportunidade.objects.filter(pk=pk).delete()
    return redirect('oportunidades')


@login_required(login_url='login')
@require_POST
@permission_required('gestao.change_oportunidade', raise_exception=True)
def oportunidade_convert_orcamento(request, pk):
    if not request.user.has_perm('gestao.add_orcamento'):
        raise PermissionDenied
    oportunidade = get_object_or_404(Oportunidade.objects.select_related('cliente'), pk=pk)
    if oportunidade.etapa != 'aprovado':
        messages.error(request, 'A oportunidade precisa estar aprovada para virar orçamento.')
        return redirect('oportunidades')
    if hasattr(oportunidade, 'orcamento_convertido'):
        messages.info(request, 'Esta oportunidade já foi convertida em orçamento.')
        return redirect('oportunidades')
    with transaction.atomic():
        orcamento = Orcamento.objects.create(
            cliente=oportunidade.cliente,
            data_orcamento=timezone.localdate(),
            descricao=oportunidade.titulo,
            valor=oportunidade.valor_estimado or 0,
            oportunidade=oportunidade,
        )
    messages.success(request, f'Orçamento {orcamento.pk} criado com sucesso.')
    return redirect('oportunidades')


@login_required(login_url='login')
@permission_required('gestao.view_falta', raise_exception=True)
def faltas(request):
    registros = Falta.objects.filter(ativo=True).select_related('funcionario').order_by('-data')
    return render(request, 'gestao/lista.html', {'titulo': 'Faltas', 'registros': registros, 'tipo': 'falta'})


@login_required(login_url='login')
@permission_required('gestao.add_falta', raise_exception=True)
def falta_create(request):
    if request.method == 'POST':
        form = FaltaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('faltas')
    else:
        form = FaltaForm()
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Nova Falta'})


@login_required(login_url='login')
@permission_required('gestao.change_falta', raise_exception=True)
def falta_update(request, pk):
    obj = get_object_or_404(Falta, pk=pk)
    if request.method == 'POST':
        form = FaltaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('faltas')
    else:
        form = FaltaForm(instance=obj)
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Falta'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_falta', raise_exception=True)
def falta_delete(request, pk):
    obj = get_object_or_404(Falta, pk=pk)
    obj.ativo = False
    obj.save()
    return redirect('faltas')


@login_required(login_url='login')
@permission_required('gestao.view_transacao', raise_exception=True)
def financeiro(request):
    registros = Transacao.objects.order_by('-data')
    total_entradas = registros.filter(tipo='entrada').aggregate(total=Sum('valor'))['total'] or 0
    total_saidas = registros.filter(tipo='saida').aggregate(total=Sum('valor'))['total'] or 0
    saldo = total_entradas - total_saidas
    return render(request, 'gestao/lista.html', {'titulo': 'Financeiro', 'registros': registros, 'tipo': 'financeiro', 'total_entradas': total_entradas, 'total_saidas': total_saidas, 'saldo': saldo})


@login_required(login_url='login')
def importacao_csv(request, tipo):
    config = IMPORT_CONFIG.get(tipo)
    if config is None:
        return redirect('dashboard')
    import_permissions = {
        'financeiro': 'gestao.add_transacao',
        'orcamento': 'gestao.add_orcamento',
        'material': 'gestao.add_item',
    }
    if not request.user.has_perm(import_permissions[tipo]):
        raise PermissionDenied
    form = ImportacaoCSVForm(request.POST or None, request.FILES or None)
    resultado = None
    if request.method == 'POST' and form.is_valid():
        try:
            imported, errors = import_csv(form.cleaned_data['arquivo'], tipo)
            resultado = {'imported': imported, 'errors': errors}
            if imported:
                messages.success(request, f'{imported} registro(s) importado(s) com sucesso.')
            if errors:
                messages.warning(request, f'{len(errors)} linha(s) não foram importadas.')
        except ValueError as exc:
            form.add_error('arquivo', str(exc))
    return render(request, 'gestao/importar.html', {'form': form, 'config': config, 'tipo': tipo, 'resultado': resultado})


@login_required(login_url='login')
@permission_required('gestao.add_transacao', raise_exception=True)
def transacao_create(request):
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('financeiro')
    else:
        form = TransacaoForm()
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Nova Transação'})


@login_required(login_url='login')
@permission_required('gestao.change_transacao', raise_exception=True)
def transacao_update(request, pk):
    obj = get_object_or_404(Transacao, pk=pk)
    if request.method == 'POST':
        form = TransacaoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('financeiro')
    else:
        form = TransacaoForm(instance=obj)
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Transação'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_transacao', raise_exception=True)
def transacao_delete(request, pk):
    Transacao.objects.filter(pk=pk).delete()
    return redirect('financeiro')


@login_required(login_url='login')
@permission_required('gestao.view_transacao', raise_exception=True)
def export_financeiro(request):
    queryset = Transacao.objects.all().order_by('-data')
    fields = ['descricao', 'tipo', 'categoria', 'valor', 'data']
    response = export_csv('financeiro', queryset, fields)
    if request.GET.get('format') == 'pdf':
        rows = [
            {'descricao': item.descricao, 'tipo': item.get_tipo_display(), 'categoria': item.get_categoria_display(), 'valor': str(item.valor), 'data': str(item.data)}
            for item in queryset
        ]
        pdf = build_pdf_response('Relatório Financeiro', rows)
        http_response = HttpResponse(pdf, content_type='application/pdf')
        http_response['Content-Disposition'] = 'attachment; filename="financeiro.pdf"'
        return http_response
    return response


@login_required(login_url='login')
@permission_required('gestao.view_orcamento', raise_exception=True)
def orcamentos(request):
    registros = Orcamento.objects.select_related('cliente').order_by('-data_orcamento')
    return render(request, 'gestao/lista.html', {'titulo': 'Orçamentos', 'registros': registros, 'tipo': 'orcamento'})


@login_required(login_url='login')
@permission_required('gestao.view_orcamento', raise_exception=True)
def orcamento_detail(request, pk):
    orcamento = get_object_or_404(Orcamento.objects.select_related('cliente', 'obra'), pk=pk)
    item_form = ItemOrcamentoForm()
    reajuste_form = ReajusteOrcamentoForm()
    if request.method == 'POST':
        if request.POST.get('action') == 'reajuste':
            if not request.user.has_perm('gestao.change_orcamento'):
                raise PermissionDenied
            reajuste_form = ReajusteOrcamentoForm(request.POST)
            if reajuste_form.is_valid():
                percentual = reajuste_form.cleaned_data['percentual']
                valor_anterior = orcamento.valor
                valor_novo = (valor_anterior * (Decimal('100') + percentual) / Decimal('100')).quantize(Decimal('0.01'))
                itens_snapshot = [
                    {'categoria': item.categoria, 'descricao': item.descricao, 'quantidade': str(item.quantidade), 'custo_unitario': str(item.custo_unitario), 'margem_percentual': str(item.margem_percentual)}
                    for item in orcamento.itens.all()
                ]
                with transaction.atomic():
                    orcamento.valor = valor_novo
                    orcamento.save(update_fields=['valor'])
                    VersaoOrcamento.objects.create(
                        orcamento=orcamento,
                        numero=orcamento.versoes.count() + 1,
                        valor_anterior=valor_anterior,
                        valor_novo=valor_novo,
                        reajuste_percentual=percentual,
                        motivo=reajuste_form.cleaned_data['motivo'],
                        itens_snapshot=itens_snapshot,
                        criado_por=request.user,
                    )
                    messages.success(request, 'Reajuste registrado e nova versão criada.')
                    return redirect('orcamento_detail', pk=orcamento.pk)
        elif request.user.has_perm('gestao.add_itemorcamento'):
            item_form = ItemOrcamentoForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.orcamento = orcamento
                item.save()
                messages.success(request, 'Item adicionado ao orçamento.')
                return redirect('orcamento_detail', pk=orcamento.pk)
        else:
            raise PermissionDenied
    return render(request, 'gestao/orcamento_detail.html', {'orcamento': orcamento, 'itens': orcamento.itens.all(), 'versoes': orcamento.versoes.all(), 'item_form': item_form, 'reajuste_form': reajuste_form})


@login_required(login_url='login')
@permission_required('gestao.view_orcamento', raise_exception=True)
def export_orcamento_pdf(request, pk):
    orcamento = get_object_or_404(Orcamento.objects.select_related('cliente'), pk=pk)
    rows = [
        {'categoria': item.get_categoria_display(), 'descricao': item.descricao, 'quantidade': str(item.quantidade), 'total': f'R$ {item.total:.2f}'}
        for item in orcamento.itens.all()
    ]
    rows.append({'categoria': '', 'descricao': 'Total da composição', 'quantidade': '', 'total': f'R$ {orcamento.total_composicao:.2f}'})
    pdf = build_pdf_response(f'Proposta - {orcamento.cliente}', rows)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orcamento-{orcamento.pk}.pdf"'
    return response


@login_required(login_url='login')
@permission_required('gestao.add_orcamento', raise_exception=True)
def orcamento_create(request):
    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('orcamentos')
    else:
        form = OrcamentoForm()
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Novo Orçamento'})


@login_required(login_url='login')
@permission_required('gestao.change_orcamento', raise_exception=True)
def orcamento_update(request, pk):
    obj = get_object_or_404(Orcamento, pk=pk)
    if request.method == 'POST':
        form = OrcamentoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('orcamentos')
    else:
        form = OrcamentoForm(instance=obj)
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Orçamento'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_orcamento', raise_exception=True)
def orcamento_delete(request, pk):
    Orcamento.objects.filter(pk=pk).delete()
    return redirect('orcamentos')


@login_required(login_url='login')
@permission_required('gestao.view_orcamento', raise_exception=True)
def export_orcamentos(request):
    queryset = Orcamento.objects.select_related('cliente').all().order_by('-data_orcamento')
    return export_csv('orcamentos', queryset, ['cliente', 'descricao', 'valor', 'data_orcamento'])


@login_required(login_url='login')
@permission_required('gestao.view_item', raise_exception=True)
def materiais(request):
    registros = Item.objects.order_by('nome')
    return render(request, 'gestao/lista.html', {'titulo': 'Materiais e Ferramentas', 'registros': registros, 'tipo': 'material'})


@login_required(login_url='login')
@permission_required('gestao.add_item', raise_exception=True)
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('materiais')
    else:
        form = ItemForm()
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Novo Material/Ferramenta'})


@login_required(login_url='login')
@permission_required('gestao.change_item', raise_exception=True)
def item_update(request, pk):
    obj = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('materiais')
    else:
        form = ItemForm(instance=obj)
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Material/Ferramenta'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_item', raise_exception=True)
def item_delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('materiais')


@login_required(login_url='login')
@permission_required('gestao.view_item', raise_exception=True)
def export_itens(request):
    queryset = Item.objects.all().order_by('nome')
    if request.GET.get('format') == 'pdf':
        rows = [
            {
                'nome': item.nome,
                'descricao': item.descricao,
                'quantidade_disponivel': str(item.quantidade_disponivel),
                'tipo': item.get_tipo_display(),
                'fabricante': item.fabricante,
                'data_aquisicao': str(item.data_aquisicao),
                'data_vencimento': str(item.data_vencimento) if item.data_vencimento else '-',
            }
            for item in queryset
        ]
        pdf = build_pdf_response('Relatório de Materiais e Ferramentas', rows)
        http_response = HttpResponse(pdf, content_type='application/pdf')
        http_response['Content-Disposition'] = 'attachment; filename="materiais.pdf"'
        return http_response
    return export_csv('materiais', queryset, ['nome', 'descricao', 'quantidade_disponivel', 'tipo', 'fabricante', 'data_aquisicao', 'data_vencimento'])


@login_required(login_url='login')
@permission_required('gestao.view_ponto', raise_exception=True)
def pontos(request):
    registros = Ponto.objects.select_related('funcionario').order_by('-data')
    return render(request, 'gestao/lista.html', {'titulo': 'Ponto dos Funcionários', 'registros': registros, 'tipo': 'ponto'})


@login_required(login_url='login')
@permission_required('gestao.add_ponto', raise_exception=True)
def ponto_create(request):
    if request.method == 'POST':
        form = PontoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pontos')
    else:
        form = PontoForm()
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Novo Registro de Ponto'})


@login_required(login_url='login')
@permission_required('gestao.change_ponto', raise_exception=True)
def ponto_update(request, pk):
    obj = get_object_or_404(Ponto, pk=pk)
    if request.method == 'POST':
        form = PontoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('pontos')
    else:
        form = PontoForm(instance=obj)
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Ponto'})


@login_required(login_url='login')
@require_POST
@permission_required('gestao.delete_ponto', raise_exception=True)
def ponto_delete(request, pk):
    Ponto.objects.filter(pk=pk).delete()
    return redirect('pontos')
