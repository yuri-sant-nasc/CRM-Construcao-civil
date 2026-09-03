from django.conf import settings
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


class Obra(models.Model):
    STATUS_CHOICES = [
        ('planejamento', 'Planejamento'),
        ('andamento', 'Em andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    nome = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='obras')
    endereco = models.CharField(max_length=250)
    data_inicio = models.DateField()
    data_previsao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejamento')
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_inicio', 'nome']

    def __str__(self):
        return self.nome


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

    def __str__(self):
        return self.descricao


class Orcamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    data_orcamento = models.DateField()
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    obra = models.ForeignKey(Obra, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos')

    def __str__(self):
        return self.descricao


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
