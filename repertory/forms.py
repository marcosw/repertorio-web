# -*-encoding: utf-8 -*-
from django.forms import ModelForm, Textarea, TextInput
from django_select2.widgets import Select2Widget, Select2MultipleWidget
# from bootstrap_toolkit.widgets import BootstrapDateInput
from repertory.models import Repertory, Event, Music

# Constrói o form de acordol com o modelo
class EventForm(ModelForm):
	class Meta:
		model = Event
		# Consideramos todos os atrubutos do model, exceto o user
		exclude = ('user',)
		widgets = {
			'observation' : Textarea(),
# 			'date' : DateTimeField(),
		}

class RepertoryForm(ModelForm):
	class Meta:
		model = Repertory
		# Consideramos somente os atributos abaixo do modelo
		fields = ('event','musics','involved',)

class MusicForm(ModelForm):
	class Meta:
		model = Music
		exclude = ('user','shared','approved',)
		widgets = {
			'name' : TextInput(attrs={'class': 'form-control', 'style':'width:500px', 'placeholder':'Nome da música'}),
			'firstPhrase' : TextInput(attrs={'class': 'form-control', 'style':'width:500px', 'placeholder':'Frase de início da música'}),
			'tone' : TextInput(attrs={'class': 'form-control', 'style':'width:100px', 'placeholder':'Ex: Bbm'}),
			'author' : Select2Widget(select2_options={'minimumResultsForSearch': 1}, attrs={'style':'width:400px', 'placeholder':'Selecione o autor'}),
			'musicCathegories' : Select2MultipleWidget(attrs={'style':'width:500px', 'placeholder':'Selecione categorias'}),
			'liturgicalTimes' : Select2MultipleWidget(attrs={'style':'width:500px', 'placeholder':'Selecione tempos litúrgicos'}),
			'liturgicalYears' : Select2MultipleWidget(attrs={'style':'width:500px', 'placeholder':'Selecione anos litúrgicos'}),
# 			'liturgicalYears' : HiddenInput(attrs={'class': 'form-control', 'size':60, 'placeholder':'Selecione anos litúrgicos'}),
# 			'cipherFile' : FileField(attrs={'class': 'form-control'}),
# 			'scoreFile' : FileField(attrs={'class': 'form-control'}),
# 			'tabFile' : FileField(attrs={'class': 'form-control'}),
# 			'audioFile' : FileField(attrs={'class': 'form-control'}),
		}
