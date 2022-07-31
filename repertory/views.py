# -*-encoding: utf-8 -*-
from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest

from django.core.urlresolvers import reverse
# Utilizamos serializers para transformar objetos python em outros tipos de objetos, como json.
from django.core import serializers

from django.contrib.auth.decorators import login_required, permission_required
# Utilizamos um framework do Django para tratar mensagens
from django.contrib import messages

from django.conf import settings

from forms import RepertoryForm, MusicForm, EventForm

from repertory.models import Repertory, Music, Event, Music_musicCathegory, Repertory_involved, Repertory_music, Music_liturgicalTime, Music_liturgicalYear, Notification

# Utilizamos estas classes para tratar validações de integridade referencal do banco de dados
from django.db import models
from django.db import IntegrityError
# Utilizamos "Q" em queries mais complexas, que precisam "AND" ou "OR"
from django.db.models import Q

# Adicionamos a biblioteca "os" do Python para que seja possivel juntar paths, remover arquivos carregados, etc.
# Adicionamos a biblioteca "json" para preparar dados para o formato json. 
import os, json

#teste
# from django.shortcuts import render_to_response
# from django.template import RequestContext

# Informações de DEBUG:
# Simples:
	# print "Permissão: ",request.user.has_perm('repertory.delete_music')
# Por console ("continue" continua a execução):
	# import pdb
	# pdb.set_trace()

# Para criar view de edição:
# stackoverflow.com/questions/1854237/django-edit-form-based-on-add-form

@login_required
def index(request):
	context = {'userFirstName':request.user.first_name,
		'musics_list': Music.objects.filter(
			user_id=request.user.id
			).order_by('-id')[:10],
		'repertories_list': Repertory.objects.filter(
			user_id=request.user.id
			).order_by('-id')[:10],}
	return render(request, 'repertory/index.html', context)

@login_required
def musics_list(request):

	# Inicializamos o parametro de busca principal com valor vazio 
	main_search_parameter = ""
	if request.method == 'POST':
		if request.POST['main_search_parameter']:
			main_search_parameter = request.POST['main_search_parameter']
			
		# Utilizamos "i" de "icontains" para buscas independente de caixa alta ou baixa
		musics_list = Music.objects.filter(
			Q(name__icontains=main_search_parameter) |
			Q(firstPhrase__icontains=main_search_parameter) |
			Q(author__completeName__icontains=main_search_parameter)
			).order_by('name')
	else:
		musics_list = Music.objects.all().order_by('name')

	# Permitimos que o usuário delete uma música apenas se ele tiver permissão para isso
	context = {'musics_list': musics_list,
			'count' : musics_list.count(),
			# Devolvemos à página o parametro de busca para ser mantê-lo no campo
			'main_search_parameter': main_search_parameter,
			'has_delete_permission': request.user.has_perm('repertory.delete_music')}
	return render(request, 'repertory/musics_list.html', context)

@login_required
# Caso nenhum valor venha por music_id ele assume None.
def music_add(request, music_id=None):

	if music_id is not None:
		music = get_object_or_404(Music, pk=music_id)
		sentForApproval = music.sentForApproval
	else:
		music = None

	# Caso tenhamos submetido um formulário de cadastro ou alteração.
	if request.method == 'POST':
		# Utilizamos request.FILES pois além de dados, estamos trabalhando com upload de arquivos
		form = MusicForm(request.POST, request.FILES, instance=music)
		
		if form.is_valid():
				
			music = form.save(commit=False)
			music.user = request.user
			# Ao cadastrarmos sentForApproval recebe False, ao atualizar, mantemos como se encontra.

			if music_id is None:
				music.sentForApproval = False
			else:
				# Recuperamos o valor antigo de sentForApproval para ser persisitido junto com os dados vindos do formulário
				music.sentForApproval = sentForApproval

			music.save()

			music = get_object_or_404(Music, pk=music.id)

			if music_id:
				# Removemos os relacionamentos m2m antigos para os novos os substituirem
				Music_musicCathegory.objects.filter(music__exact=music.id).delete()
				Music_liturgicalTime.objects.filter(music__exact=music.id).delete()
				Music_liturgicalYear.objects.filter(music__exact=music.id).delete()

			# Recuperamos os registros m2m selecionados no formulário, criamos um objeto para cada e os salvamos individualmente
			for musicCathegory in form.cleaned_data['musicCathegories']:
				Music_musicCathegory.objects.create(music_id=music.id, musicCathegory_id=int(musicCathegory.id))
			
			for liturgicalTime in form.cleaned_data['liturgicalTimes']:
				Music_liturgicalTime.objects.create(music_id=music.id, liturgicalTime_id=int(liturgicalTime.id))
			
			for liturgicalYear in form.cleaned_data['liturgicalYears']:
				Music_liturgicalYear.objects.create(music_id=music.id, liturgicalYear_id=int(liturgicalYear.id))
				
		  	# Criamos after_create_music_id para guardar id da música recém cadastrada e alterar função para alteração
		  	# ao persistir dados por ajax pela primeira vez.
		  	data = {'success': True, 'after_create_music_id':music.id, }
		
			# É necessário que um objeto Json seja retornado para o javascript
			# json.dumps serializa um objeto para o formato string json usando uma tagela de conversão Python/Json abaixo:
 			return HttpResponse(json.dumps(data), mimetype='application/json')

		else:
			#ensure ascii remove códigos de caracteres especiais da string
			data = json.dumps(form.errors.items(), ensure_ascii=False)
			return HttpResponseBadRequest(data, mimetype='application/json')

	else:
		# Caso abrimos pela primeira vez o formulário, para cadastro ou alteração
		form = MusicForm(instance=music)
		
	if music_id:
		context = {
			'form':form, 
			'music_id':music_id, 
			'shared_music':music.shared,
			'sent_for_approval':music.sentForApproval, 
			'has_approve_music_permission': request.user.has_perm('repertory.approve_music')
		}
	else:
		context = {'form':form,}
	return render(request, 'repertory/music_add.html', context)

# Utilizamos esta função para fazer o download de um arquivo de música
@login_required
def music_file_download(request, music_id, music_file_type):
	import mimetypes 
	from os import path

	# Aqui Recuperamos o objeto música pelo atributo music_id passado pela url
	# Levantamos uma tela 404 se o id não existir
	music = get_object_or_404(Music, pk=music_id)

	# Identificamos que tipo de arquivo de música é para fazer o download corretamente
	if music_file_type == '1':
 		music_file = music.cipherFile
 	elif music_file_type == '2':
		music_file = music.scoreFile
	elif music_file_type == '3':
		music_file = music.tabFile
	elif music_file_type == '4':
		music_file = music.audioFile
	else:
  		# Utilizamos raise para levantar uma página 404 através do método Http404()
		raise Http404() # Disparamos tela 404 caso o número não esteja entre 1 e 4

	# Montamos o caminho do arquivo
	# arquivo = "%s/%s" % (settings.MEDIA_ROOT, music_file,)
	arquivo = os.path.join(settings.MEDIA_ROOT, str(music_file))

	# Disparamos tela 404 caso o arquivo não exista
  	if not (path.exists(arquivo)):
		raise Http404()

	mimetype, encoding = mimetypes.guess_type(arquivo)
	if mimetype is None:
		mimetype = 'application/force-download'
	file = arquivo.split("/")[-1]
	response = HttpResponse(open(arquivo, 'r').read())
	response['Content-Type'] = mimetype
	response['Pragma'] = 'public'
	response['Expires'] = '0'
	response['Cache-Control'] = 'must-revalidate, post-check=0, pre-check=0'
	response['Content-Disposition'] = 'attachment; filename=%s' % file
	response['Content-Transfer-Encoding'] = 'binary'
	response['Content-Length'] = str(path.getsize(arquivo))
	return response

@login_required
def music_detail(request, music_id):
	music = get_object_or_404(Music, pk=music_id)

	# Capturamos apenas o nome do arquivo e não seu caminho completo
	if music.cipherFile:
		music.cipherFile = str(music.cipherFile).split("/")[-1]
	if music.scoreFile:
		music.scoreFile = str(music.scoreFile).split("/")[-1]
	if music.tabFile:
		music.tabFile = str(music.tabFile).split("/")[-1]
	if music.audioFile:
		music.audioFile = str(music.audioFile).split("/")[-1]

	context = {'music':music}
	return render(request, 'repertory/music_detail.html', context)

# TODO adicionar na mensagem de remoção: Deseja realmente remover o registro e os arquivos associados?
@login_required
@permission_required('repertory.delete_music', raise_exception=True)
def music_remove(request, music_id):
	try:
		music = get_object_or_404(Music, pk=music_id)
	    # Removemos a música antes de removermos os arquivos dela, pois caso
	    # não seja possivel executar o try com music.delete() os arquivos permanecem.
		music.delete()
		# Se o arquivo existir, removemos o objeto do banco e fisicamente.
		# Foi foi possivel utilizar o método delete() do objeto File neste caso, ele não removia diretamente.
		if music.cipherFile:			
			os.remove(os.path.join(settings.MEDIA_ROOT, str(music.cipherFile)))
		if music.scoreFile:
			os.remove(os.path.join(settings.MEDIA_ROOT, str(music.scoreFile)))
		if music.tabFile:
			os.remove(os.path.join(settings.MEDIA_ROOT, str(music.tabFile)))
		if music.audioFile:
			os.remove(os.path.join(settings.MEDIA_ROOT, str(music.audioFile)))
	except models.ProtectedError:
		messages.info(request, 'Existem registros relacionados a esta música. Não é possivel removê-la.')
	return HttpResponseRedirect(reverse('repertory:musics_list'))

	# Retornamos para a tela de listagem de músicas
	return HttpResponseRedirect(reverse('repertory:musics_list'))

@login_required
def music_share(request, music_id):
	# Alteramos o atributo de envio para aprovação como verdadeiro.
	music = Music.objects.get(pk=music_id)
	if music.sentForApproval == False:
		music.sentForApproval = True
		music.save()
		# Geramos notificação aos aprovadores.
		# criar permissão music_approver e criar uma notificação para cada um dos usuários com este perfil.
		# for
		Notification.objects.create(
			music_id=music_id,
			receiver_id=1,
			systemMessage=request.user.get_full_name() + unicode(u' está aguardando aprovação de música.'),
			userMessage=request.POST['messageToUser']
		)
		data = {'success': True }
	else:
		data = {'success': False }
	
	return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required
@permission_required('repertory.approve_music', raise_exception=True)
def music_approve(request, music_id):
	# Alteramos o atributo de envio para aprovação como verdadeiro.
	music = Music.objects.get(pk=music_id)
	if music.shared == False:
		music.shared = True
		music.save()

		Notification.objects.create(
			music_id=music_id,
			receiver_id=music.user_id,
			systemMessage=request.user.get_full_name() + unicode(u' aprovou sua música! Todos os usuário de agora em diante poderão vê-la.'),
			userMessage=request.POST['messageToUser']
		)
		data = {'success': True }
	else:
		data = {'success': False }
	
	return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required
def repertory_add(request, repertory_id=None):

	if repertory_id is not None:
		repertory = get_object_or_404(Repertory, pk=repertory_id)
	else:
		repertory = None

	if request.method == 'POST':
		form = RepertoryForm(request.POST, instance=repertory)
		if form.is_valid():
			repertory = form.save(commit=False)
			repertory.user = request.user
			repertory.save()

			repertory = get_object_or_404(Repertory, pk=repertory.id)   

			# Caso estejamos alterando, removemos os relacionamentos m2m antigos para os novos os substituirem
			if repertory_id:
				# Deletamos os objetos antigos m2m
				Repertory_involved.objects.filter(repertory__exact=repertory.id).delete()
				Repertory_music.objects.filter(repertory__exact=repertory.id).delete()

			for involved in form.cleaned_data['involved']:
				Repertory_involved.objects.create(repertory_id=repertory.id, user_id=int(involved.id))

			for music in form.cleaned_data['musics']:
				Repertory_music.objects.create(repertory_id=repertory.id, music_id=int(music.id))

			messages.success(request, 'Salvo com sucesso!')

			return HttpResponseRedirect(reverse('repertory:repertories_list'))
	else:
		form = RepertoryForm(instance=repertory)

	if repertory_id:
		context = {'form':form, 'repertory_id':repertory_id,}
	else:
		context = {'form':form,}
	return render(request, 'repertory/repertory_add.html', context)

@login_required
def repertories_list(request):
	context = {'repertories_list': Repertory.objects.all()}
	return render(request, 'repertory/repertories_list.html', context)

@login_required
def repertory_detail(request, repertory_id):
	repertory = get_object_or_404(Repertory, pk=repertory_id)
	context = {'repertory':repertory}
	return render(request, 'repertory/repertory_detail.html', context)

@login_required
def repertory_remove(request, repertory_id):	
	repertory = get_object_or_404(Repertory, pk=repertory_id)
	repertory.delete()
	return HttpResponseRedirect(reverse('repertory:repertories_list'))

@login_required
def events_list(request):
	context = {'events_list': Event.objects.all()}
	return render(request, 'repertory/events_list.html', context)

@login_required
def event_detail(request, event_id):
	event = get_object_or_404(Event, pk=event_id)
	return render(request, 'repertory/event_detail.html', {'event':event})

@login_required
def event_add(request, event_id=None):

	if event_id is not None:
		event = get_object_or_404(Event, pk=event_id)
	else:
		event = None
	
	if request.method == 'POST':
		form = EventForm(request.POST, instance=event)
		if form.is_valid():
			event = form.save(commit=False)
			event.user = request.user
			event.save()
			return HttpResponseRedirect(reverse('repertory:events_list'))
	else:
		form = EventForm(instance=event)
	
	if event_id:
		context = {'form':form, 'event_id':event_id,}
	else:
		context = {'form':form,}
	return render(request, 'repertory/event_add.html', context)

@login_required
def event_remove(request, event_id):	
	try:
		event = get_object_or_404(Event, pk=event_id)
		event.delete()
		return HttpResponseRedirect(reverse('repertory:events_list'))
	except models.ProtectedError:
		messages.info(request, 'Existem registros relacionados a este evento. Não é possivel removê-lo.')
	return HttpResponseRedirect(reverse('repertory:events_list'))

@login_required
def notifications(request):	
	notifications = Notification.objects.filter(
		receiver=request.user.id).filter(
		seen=False)
	response = serializers.serialize("json", notifications)
	return HttpResponse(response, mimetype="text/javascript")

@login_required
def notifications_count(request):	
	notifications_count = Notification.objects.filter(
		receiver=request.user.id).filter(
		seen=False).count()
	return HttpResponse(notifications_count, mimetype="text/javascript")
