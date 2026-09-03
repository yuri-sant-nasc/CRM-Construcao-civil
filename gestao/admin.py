from django.contrib import admin

from .models import AuditLog, Cliente, DiarioObra, Falta, FotoObra, Funcionario, Item, ItemOrcamento, Obra, Ocorrencia, Oportunidade, Orcamento, Pagamento, Transacao, VersaoOrcamento


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'path', 'status_code', 'ip_address')
    list_filter = ('action', 'status_code', 'created_at')
    search_fields = ('path', 'user__username', 'ip_address')
    readonly_fields = ('created_at', 'user', 'action', 'path', 'status_code', 'ip_address')


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'responsavel', 'status', 'percentual_concluido', 'data_inicio', 'data_previsao')
    list_filter = ('status', 'data_inicio')
    search_fields = ('nome', 'cliente__nome_completo', 'cliente__empresa')


@admin.register(DiarioObra)
class DiarioObraAdmin(admin.ModelAdmin):
    list_display = ('obra', 'data', 'autor', 'criado_em')
    list_filter = ('data',)


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'obra', 'status', 'autor', 'criado_em')
    list_filter = ('status', 'criado_em')
    search_fields = ('titulo', 'descricao', 'obra__nome')


@admin.register(FotoObra)
class FotoObraAdmin(admin.ModelAdmin):
    list_display = ('obra', 'legenda', 'autor', 'enviada_em')


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'funcao', 'cpf', 'cidade', 'ativo')
    list_filter = ('ativo', 'estado')
    search_fields = ('nome_completo', 'cpf', 'email')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'empresa', 'cnpj', 'telefone', 'ativo')
    list_filter = ('ativo', 'estado')
    search_fields = ('nome_completo', 'empresa', 'cnpj', 'email')


@admin.register(Oportunidade)
class OportunidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'etapa', 'origem', 'valor_estimado', 'data_previsao_fechamento', 'atualizado_em')
    list_filter = ('etapa', 'origem', 'data_previsao_fechamento')
    search_fields = ('titulo', 'cliente__nome_completo', 'cliente__empresa')


@admin.register(Falta)
class FaltaAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'motivo', 'status', 'presente')
    list_filter = ('status', 'presente', 'data')
    search_fields = ('funcionario__nome_completo', 'motivo')


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'categoria', 'obra', 'valor', 'status', 'data_vencimento')
    list_filter = ('tipo', 'categoria', 'status', 'data')


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('transacao', 'valor', 'data', 'criado_por')
    list_filter = ('data',)

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'obra', 'descricao', 'valor', 'data_orcamento')
    list_filter = ('data_orcamento',)
    search_fields = ('descricao', 'cliente__nome_completo')


@admin.register(ItemOrcamento)
class ItemOrcamentoAdmin(admin.ModelAdmin):
    list_display = ('orcamento', 'categoria', 'descricao', 'quantidade', 'custo_unitario', 'margem_percentual')
    list_filter = ('categoria',)


@admin.register(VersaoOrcamento)
class VersaoOrcamentoAdmin(admin.ModelAdmin):
    list_display = ('orcamento', 'numero', 'valor_anterior', 'valor_novo', 'reajuste_percentual', 'criado_por', 'criado_em')
    readonly_fields = ('orcamento', 'numero', 'valor_anterior', 'valor_novo', 'reajuste_percentual', 'motivo', 'itens_snapshot', 'criado_por', 'criado_em')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'obra', 'fabricante', 'quantidade_disponivel', 'quantidade_minima', 'data_aquisicao', 'data_vencimento')
    list_filter = ('fabricante',)
    search_fields = ('nome', 'fabricante', 'descricao')
