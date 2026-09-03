from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.cache import cache
from django.utils.dateparse import parse_date

from .exports import export_csv
from .forms import (
    ClienteForm,
    FaltaForm,
    FuncionarioForm,
    ItemForm,
    LoginForm,
    ImportacaoCSVForm,
    ObraForm,
    OrcamentoForm,
    PontoForm,
    TransacaoForm,
)
from .models import Cliente, Falta, Funcionario, Item, Obra, Orcamento, Ponto, Transacao
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
def funcionarios(request):
    registros = Funcionario.objects.filter(ativo=True).order_by('-id')
    return render(request, 'gestao/lista.html', {'titulo': 'Funcionários', 'registros': registros, 'tipo': 'funcionario'})


@login_required(login_url='login')
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
def funcionario_delete(request, pk):
    obj = get_object_or_404(Funcionario, pk=pk)
    obj.ativo = False
    obj.save()
    return redirect('funcionarios')


@login_required(login_url='login')
def clientes(request):
    registros = Cliente.objects.filter(ativo=True).order_by('-id')
    return render(request, 'gestao/lista.html', {'titulo': 'Clientes', 'registros': registros, 'tipo': 'cliente'})


@login_required(login_url='login')
def obras(request):
    registros = Obra.objects.select_related('cliente').all()
    return render(request, 'gestao/lista.html', {'titulo': 'Obras', 'registros': registros, 'tipo': 'obra'})


@login_required(login_url='login')
def obra_create(request):
    form = ObraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('obras')
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Nova Obra'})


@login_required(login_url='login')
def obra_update(request, pk):
    obj = get_object_or_404(Obra, pk=pk)
    form = ObraForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('obras')
    return render(request, 'gestao/formulario.html', {'form': form, 'titulo': 'Editar Obra'})


@login_required(login_url='login')
@require_POST
def obra_delete(request, pk):
    Obra.objects.filter(pk=pk).delete()
    return redirect('obras')


@login_required(login_url='login')
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
def cliente_delete(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    obj.ativo = False
    obj.save()
    return redirect('clientes')


@login_required(login_url='login')
def faltas(request):
    registros = Falta.objects.filter(ativo=True).select_related('funcionario').order_by('-data')
    return render(request, 'gestao/lista.html', {'titulo': 'Faltas', 'registros': registros, 'tipo': 'falta'})


@login_required(login_url='login')
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
def falta_delete(request, pk):
    obj = get_object_or_404(Falta, pk=pk)
    obj.ativo = False
    obj.save()
    return redirect('faltas')


@login_required(login_url='login')
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
def transacao_delete(request, pk):
    Transacao.objects.filter(pk=pk).delete()
    return redirect('financeiro')


@login_required(login_url='login')
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
def orcamentos(request):
    registros = Orcamento.objects.select_related('cliente').order_by('-data_orcamento')
    return render(request, 'gestao/lista.html', {'titulo': 'Orçamentos', 'registros': registros, 'tipo': 'orcamento'})


@login_required(login_url='login')
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
def orcamento_delete(request, pk):
    Orcamento.objects.filter(pk=pk).delete()
    return redirect('orcamentos')


@login_required(login_url='login')
def export_orcamentos(request):
    queryset = Orcamento.objects.select_related('cliente').all().order_by('-data_orcamento')
    return export_csv('orcamentos', queryset, ['cliente', 'descricao', 'valor', 'data_orcamento'])


@login_required(login_url='login')
def materiais(request):
    registros = Item.objects.order_by('nome')
    return render(request, 'gestao/lista.html', {'titulo': 'Materiais e Ferramentas', 'registros': registros, 'tipo': 'material'})


@login_required(login_url='login')
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
def item_delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('materiais')


@login_required(login_url='login')
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
def pontos(request):
    registros = Ponto.objects.select_related('funcionario').order_by('-data')
    return render(request, 'gestao/lista.html', {'titulo': 'Ponto dos Funcionários', 'registros': registros, 'tipo': 'ponto'})


@login_required(login_url='login')
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
def ponto_delete(request, pk):
    Ponto.objects.filter(pk=pk).delete()
    return redirect('pontos')
