from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('funcionarios/', views.funcionarios, name='funcionarios'),
    path('funcionarios/novo/', views.funcionario_create, name='funcionario_create'),
    path('funcionarios/<int:pk>/editar/', views.funcionario_update, name='funcionario_update'),
    path('funcionarios/<int:pk>/excluir/', views.funcionario_delete, name='funcionario_delete'),

    path('clientes/', views.clientes, name='clientes'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/excluir/', views.cliente_delete, name='cliente_delete'),

    path('oportunidades/', views.oportunidades, name='oportunidades'),
    path('oportunidades/nova/', views.oportunidade_create, name='oportunidade_create'),
    path('oportunidades/<int:pk>/editar/', views.oportunidade_update, name='oportunidade_update'),
    path('oportunidades/<int:pk>/excluir/', views.oportunidade_delete, name='oportunidade_delete'),
    path('oportunidades/<int:pk>/converter-orcamento/', views.oportunidade_convert_orcamento, name='oportunidade_convert_orcamento'),

    path('obras/', views.obras, name='obras'),
    path('obras/novo/', views.obra_create, name='obra_create'),
    path('obras/<int:pk>/editar/', views.obra_update, name='obra_update'),
    path('obras/<int:pk>/operacao/', views.obra_operacao, name='obra_operacao'),
    path('obras/<int:pk>/excluir/', views.obra_delete, name='obra_delete'),
    path('fotos-obras/<int:pk>/download/', views.foto_obra_download, name='foto_obra_download'),

    path('faltas/', views.faltas, name='faltas'),
    path('faltas/novo/', views.falta_create, name='falta_create'),
    path('faltas/<int:pk>/editar/', views.falta_update, name='falta_update'),
    path('faltas/<int:pk>/excluir/', views.falta_delete, name='falta_delete'),

    path('financeiro/', views.financeiro, name='financeiro'),
    path('financeiro/painel/', views.painel_financeiro, name='painel_financeiro'),
    path('financeiro/novo/', views.transacao_create, name='transacao_create'),
    path('financeiro/<int:pk>/editar/', views.transacao_update, name='transacao_update'),
    path('financeiro/<int:pk>/excluir/', views.transacao_delete, name='transacao_delete'),
    path('financeiro/<int:pk>/pagamento/', views.pagamento_create, name='pagamento_create'),
    path('financeiro/exportar/', views.export_financeiro, name='export_financeiro'),
    path('financeiro/importar/', views.importacao_csv, {'tipo': 'financeiro'}, name='import_financeiro'),

    path('orcamentos/', views.orcamentos, name='orcamentos'),
    path('orcamentos/<int:pk>/', views.orcamento_detail, name='orcamento_detail'),
    path('orcamentos/<int:pk>/proposta.pdf', views.export_orcamento_pdf, name='export_orcamento_pdf'),
    path('orcamentos/novo/', views.orcamento_create, name='orcamento_create'),
    path('orcamentos/<int:pk>/editar/', views.orcamento_update, name='orcamento_update'),
    path('orcamentos/<int:pk>/excluir/', views.orcamento_delete, name='orcamento_delete'),
    path('orcamentos/exportar/', views.export_orcamentos, name='export_orcamentos'),
    path('orcamentos/importar/', views.importacao_csv, {'tipo': 'orcamento'}, name='import_orcamentos'),

    path('materiais/', views.materiais, name='materiais'),
    path('materiais/novo/', views.item_create, name='item_create'),
    path('materiais/<int:pk>/editar/', views.item_update, name='item_update'),
    path('materiais/<int:pk>/excluir/', views.item_delete, name='item_delete'),
    path('materiais/exportar/', views.export_itens, name='export_itens'),
    path('materiais/importar/', views.importacao_csv, {'tipo': 'material'}, name='import_materiais'),

    path('pontos/', views.pontos, name='pontos'),
    path('pontos/novo/', views.ponto_create, name='ponto_create'),
    path('pontos/<int:pk>/editar/', views.ponto_update, name='ponto_update'),
    path('pontos/<int:pk>/excluir/', views.ponto_delete, name='ponto_delete'),
]
