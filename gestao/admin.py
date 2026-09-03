from django.contrib import admin

from .models import AuditLog, Cliente, Falta, Funcionario, Item, Obra, Orcamento, Transacao


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'path', 'status_code', 'ip_address')
    list_filter = ('action', 'status_code', 'created_at')
    search_fields = ('path', 'user__username', 'ip_address')
    readonly_fields = ('created_at', 'user', 'action', 'path', 'status_code', 'ip_address')


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'status', 'data_inicio', 'data_previsao')
    list_filter = ('status', 'data_inicio')
    search_fields = ('nome', 'cliente__nome_completo', 'cliente__empresa')


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


@admin.register(Falta)
class FaltaAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'motivo', 'status', 'presente')
    list_filter = ('status', 'presente', 'data')
    search_fields = ('funcionario__nome_completo', 'motivo')


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'categoria', 'obra', 'valor', 'data')
    list_filter = ('tipo', 'categoria', 'data')


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'obra', 'descricao', 'valor', 'data_orcamento')
    list_filter = ('data_orcamento',)
    search_fields = ('descricao', 'cliente__nome_completo')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'obra', 'fabricante', 'quantidade_disponivel', 'quantidade_minima', 'data_aquisicao', 'data_vencimento')
    list_filter = ('fabricante',)
    search_fields = ('nome', 'fabricante', 'descricao')
