from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Cliente, DiarioObra, Falta, FotoObra, Funcionario, Item, ItemOrcamento, Obra, Ocorrencia, Oportunidade, Orcamento, Ponto, Transacao


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuário', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ImportacaoCSVForm(forms.Form):
    arquivo = forms.FileField(
        label='Arquivo CSV',
        help_text='Use UTF-8 e inclua a primeira linha com os nomes das colunas.',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.csv,text/csv'}),
    )


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            'usuario', 'nome_completo', 'funcao', 'estado_civil', 'data_admissao',
            'data_nascimento', 'cpf', 'bairro', 'rua', 'numero', 'cidade', 'estado',
            'celular', 'email', 'ativo'
        ]
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            **{field: forms.TextInput(attrs={'class': 'form-control'}) for field in ['usuario', 'nome_completo', 'funcao', 'estado_civil', 'cpf', 'bairro', 'rua', 'numero', 'cidade', 'estado', 'celular', 'email']},
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nome_completo', 'empresa', 'cargo', 'cnpj', 'contato_anterior',
            'descricao_pedido', 'bairro', 'rua', 'numero', 'cidade', 'estado',
            'telefone', 'email', 'ativo'
        ]
        widgets = {
            'contato_anterior': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao_pedido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            **{field: forms.TextInput(attrs={'class': 'form-control'}) for field in ['nome_completo', 'empresa', 'cargo', 'cnpj', 'bairro', 'rua', 'numero', 'cidade', 'estado', 'telefone', 'email']},
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OportunidadeForm(forms.ModelForm):
    class Meta:
        model = Oportunidade
        fields = [
            'cliente', 'responsavel', 'titulo', 'etapa', 'origem', 'valor_estimado',
            'probabilidade_fechamento', 'data_previsao_fechamento', 'data_proximo_contato',
            'observacoes', 'motivo_perda',
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'responsavel': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'etapa': forms.Select(attrs={'class': 'form-control'}),
            'origem': forms.Select(attrs={'class': 'form-control'}),
            'valor_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'probabilidade_fechamento': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'data_previsao_fechamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_proximo_contato': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'motivo_perda': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        probability = cleaned_data.get('probabilidade_fechamento')
        if probability is not None and probability > 100:
            self.add_error('probabilidade_fechamento', 'A probabilidade deve estar entre 0 e 100.')
        if cleaned_data.get('etapa') == 'perdido' and not cleaned_data.get('motivo_perda'):
            self.add_error('motivo_perda', 'Informe o motivo da perda.')
        return cleaned_data


class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = ['nome', 'cliente', 'responsavel', 'equipe', 'endereco', 'data_inicio', 'data_previsao', 'status', 'percentual_concluido', 'observacoes']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'responsavel': forms.Select(attrs={'class': 'form-control'}),
            'equipe': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_previsao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'percentual_concluido': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_percentual_concluido(self):
        percentual = self.cleaned_data['percentual_concluido']
        if percentual > 100:
            raise forms.ValidationError('O percentual deve estar entre 0 e 100.')
        return percentual


class DiarioObraForm(forms.ModelForm):
    class Meta:
        model = DiarioObra
        fields = ['obra', 'data', 'resumo']
        widgets = {'obra': forms.Select(attrs={'class': 'form-control'}), 'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 'resumo': forms.Textarea(attrs={'class': 'form-control', 'rows': 5})}


class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['obra', 'titulo', 'descricao', 'status']
        widgets = {'obra': forms.Select(attrs={'class': 'form-control'}), 'titulo': forms.TextInput(attrs={'class': 'form-control'}), 'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), 'status': forms.Select(attrs={'class': 'form-control'})}


class FotoObraForm(forms.ModelForm):
    class Meta:
        model = FotoObra
        fields = ['obra', 'arquivo', 'legenda']
        widgets = {'obra': forms.Select(attrs={'class': 'form-control'}), 'arquivo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/webp'}), 'legenda': forms.TextInput(attrs={'class': 'form-control'})}


class FaltaForm(forms.ModelForm):
    class Meta:
        model = Falta
        fields = ['funcionario', 'data', 'presente', 'motivo', 'status', 'ativo']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'funcionario': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'presente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['valor', 'data', 'descricao', 'tipo', 'categoria', 'obra']
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'obra': forms.Select(attrs={'class': 'form-control'}),
        }


class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['cliente', 'obra', 'data_orcamento', 'descricao', 'valor']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'data_orcamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'obra': forms.Select(attrs={'class': 'form-control'}),
        }


class ItemOrcamentoForm(forms.ModelForm):
    class Meta:
        model = ItemOrcamento
        fields = ['categoria', 'descricao', 'quantidade', 'custo_unitario', 'margem_percentual']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0.001'}),
            'custo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'margem_percentual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class ReajusteOrcamentoForm(forms.Form):
    percentual = forms.DecimalField(min_value=0.01, max_value=1000, max_digits=7, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}))
    motivo = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'class': 'form-control'}))


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nome', 'descricao', 'quantidade_disponivel', 'quantidade_minima', 'tipo', 'fabricante', 'data_aquisicao', 'data_vencimento', 'obra']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade_disponivel': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantidade_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'data_aquisicao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'obra': forms.Select(attrs={'class': 'form-control'}),
        }


class PontoForm(forms.ModelForm):
    class Meta:
        model = Ponto
        fields = ['funcionario', 'data', 'entrada', 'saida', 'observacao']
        widgets = {
            'funcionario': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'entrada': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'saida': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'observacao': forms.TextInput(attrs={'class': 'form-control'}),
        }
