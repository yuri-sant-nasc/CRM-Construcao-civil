from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class PessoaBase(models.Model):
    bairro = models.CharField(max_length=120)
    rua = models.CharField(max_length=160)
    numero = models.CharField(max_length=20)
    cidade = models.CharField(max_length=120)
    estado = models.CharField(max_length=2)
    ativo = models.BooleanField(default=True)

    class Meta:
        abstract = True


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    status_code = models.PositiveSmallIntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Funcionario(PessoaBase):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='funcionario')
    nome_completo = models.CharField(max_length=200)
    funcao = models.CharField(max_length=120)
    estado_civil = models.CharField(max_length=40)
    data_admissao = models.DateField()
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11, unique=True)
    celular = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'

    def __str__(self):
        return self.nome_completo


class Cliente(PessoaBase):
    nome_completo = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200)
    cargo = models.CharField(max_length=120)
    cnpj = models.CharField(max_length=14, unique=True)
    contato_anterior = models.DateField(null=True, blank=True)
    descricao_pedido = models.TextField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome_completo


class Oportunidade(models.Model):
    ETAPA_CHOICES = [
        ('novo', 'Novo contato'),
        ('visita', 'Visita técnica'),
        ('orcamento', 'Orçamento'),
        ('negociacao', 'Negociação'),
        ('aprovado', 'Aprovado'),
        ('perdido', 'Perdido'),
    ]
    ORIGEM_CHOICES = [
        ('indicacao', 'Indicação'),
        ('site', 'Site'),
        ('redes_sociais', 'Redes sociais'),
        ('prospeccao', 'Prospecção'),
        ('outro', 'Outro'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='oportunidades')
    titulo = models.CharField(max_length=200)
    responsavel = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True, related_name='oportunidades')
    etapa = models.CharField(max_length=20, choices=ETAPA_CHOICES, default='novo')
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='outro')
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    probabilidade_fechamento = models.PositiveSmallIntegerField(default=0)
    data_previsao_fechamento = models.DateField(null=True, blank=True)
    data_proximo_contato = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    motivo_perda = models.CharField(max_length=250, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-atualizado_em', 'titulo']

    def __str__(self):
        return self.titulo


class HistoricoOportunidade(models.Model):
    oportunidade = models.ForeignKey(Oportunidade, on_delete=models.CASCADE, related_name='historico')
    etapa_anterior = models.CharField(max_length=20, blank=True)
    etapa_nova = models.CharField(max_length=20)
    alterado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    alterado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-alterado_em']


class Obra(models.Model):
    STATUS_CHOICES = [
        ('planejamento', 'Planejamento'),
        ('andamento', 'Em andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    nome = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='obras')
    responsavel = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True, related_name='obras_responsavel')
    equipe = models.ManyToManyField(Funcionario, blank=True, related_name='obras_equipe')
    endereco = models.CharField(max_length=250)
    data_inicio = models.DateField()
    data_previsao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejamento')
    percentual_concluido = models.PositiveSmallIntegerField(default=0)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_inicio', 'nome']

    def __str__(self):
        return self.nome

    def clean(self):
        if self.percentual_concluido > 100:
            raise ValidationError({'percentual_concluido': 'O percentual deve estar entre 0 e 100.'})
        if self.status == 'concluida' and self.percentual_concluido < 100:
            raise ValidationError({'status': 'Uma obra concluída deve estar com 100% de conclusão.'})


class DiarioObra(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name='diarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateField(default=timezone.localdate)
    resumo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-criado_em']

    def __str__(self):
        return f'{self.obra} - {self.data}'


class Ocorrencia(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_tratamento', 'Em tratamento'),
        ('resolvida', 'Resolvida'),
    ]

    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name='ocorrencias')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    criado_em = models.DateTimeField(auto_now_add=True)
    resolvido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo


def validate_photo_size(upload):
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError('A foto deve ter no máximo 5 MB.')


class FotoObra(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name='fotos')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    arquivo = models.FileField(
        upload_to='obras/fotos/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']), validate_photo_size],
    )
    legenda = models.CharField(max_length=200, blank=True)
    enviada_em = models.DateTimeField(auto_now_add=True)


class Falta(models.Model):
    STATUS_CHOICES = [
        ('justificada', 'Justificada'),
        ('nao_justificada', 'Não justificada'),
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='faltas')
    data = models.DateField()
    presente = models.BooleanField(default=False)
    motivo = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default='nao_justificada')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.funcionario} - {self.data}'


class Ponto(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='pontos')
    data = models.DateField()
    entrada = models.DateTimeField(null=True, blank=True, default=timezone.now)
    saida = models.DateTimeField(null=True, blank=True, default=timezone.now)
    observacao = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.funcionario} - {self.data}'


class Transacao(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    CATEGORIA_CHOICES = [
        ('salarios', 'Salários'),
        ('materiais', 'Materiais'),
        ('aluguel', 'Aluguel'),
        ('outros', 'Outros'),
    ]

    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()
    descricao = models.CharField(max_length=200)
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    obra = models.ForeignKey(Obra, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes')
    data_vencimento = models.DateField(null=True, blank=True)
    centro_custo = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=[('pendente', 'Pendente'), ('parcial', 'Parcial'), ('pago', 'Pago'), ('cancelado', 'Cancelado')], default='pendente')

    def __str__(self):
        return self.descricao

    @property
    def total_pago(self):
        return sum((pagamento.valor for pagamento in self.pagamentos.all()), Decimal('0.00'))

    @property
    def saldo_aberto(self):
        return max(Decimal(self.valor) - self.total_pago, Decimal('0.00'))


class Pagamento(models.Model):
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='pagamentos')
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField(default=timezone.localdate)
    observacao = models.CharField(max_length=250, blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        valor = Decimal(self.valor)
        if valor <= 0:
            raise ValidationError({'valor': 'O pagamento deve ser maior que zero.'})
        if self.transacao_id and valor > self.transacao.saldo_aberto:
            raise ValidationError({'valor': 'O pagamento não pode ultrapassar o saldo aberto.'})


class Orcamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    data_orcamento = models.DateField()
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    obra = models.ForeignKey(Obra, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos')
    oportunidade = models.OneToOneField(Oportunidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamento_convertido')

    def __str__(self):
        return self.descricao

    @property
    def total_composicao(self):
        return sum((item.total for item in self.itens.all()), 0)


class ItemOrcamento(models.Model):
    CATEGORIA_CHOICES = [
        ('material', 'Material'),
        ('mao_de_obra', 'Mão de obra'),
        ('equipamento', 'Equipamento'),
        ('servico', 'Serviço'),
    ]

    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descricao = models.CharField(max_length=200)
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    margem_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def custo_total(self):
        return self.quantidade * self.custo_unitario

    @property
    def total(self):
        return self.custo_total * (1 + self.margem_percentual / 100)

    def clean(self):
        errors = {}
        if self.quantidade <= 0:
            errors['quantidade'] = 'A quantidade deve ser maior que zero.'
        if self.custo_unitario < 0:
            errors['custo_unitario'] = 'O custo unitário não pode ser negativo.'
        if self.margem_percentual < 0:
            errors['margem_percentual'] = 'A margem não pode ser negativa.'
        if errors:
            raise ValidationError(errors)


class VersaoOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='versoes')
    numero = models.PositiveIntegerField()
    valor_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    valor_novo = models.DecimalField(max_digits=12, decimal_places=2)
    reajuste_percentual = models.DecimalField(max_digits=7, decimal_places=2)
    motivo = models.CharField(max_length=250)
    itens_snapshot = models.JSONField(default=list)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-numero']
        constraints = [models.UniqueConstraint(fields=['orcamento', 'numero'], name='unique_orcamento_versao')]


class Item(models.Model):
    TIPO_CHOICES = [
        ('material', 'Material'),
        ('ferramenta', 'Ferramenta'),
        ('epi', 'EPI'),
    ]

    nome = models.CharField(max_length=150)
    descricao = models.CharField(max_length=250)
    quantidade_disponivel = models.IntegerField(default=0)
    quantidade_minima = models.PositiveIntegerField(default=0)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='material')
    fabricante = models.CharField(max_length=120)
    data_aquisicao = models.DateField()
    data_vencimento = models.DateField(null=True, blank=True)
    obra = models.ForeignKey(Obra, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens')

    def __str__(self):
        return self.nome
