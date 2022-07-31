# -*-encoding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('',
	# tela principal. Aqui chamamos as views, reponsáveis por renderizar os templates.
	url(r'^$', 'repertory.views.index', name='index'),
	# telas músicas
	url(r'^musicas/$', 'repertory.views.musics_list', name='musics_list'),
	url(r'^musicas/cadastro/$', 'repertory.views.music_add', name='music_add'),
	url(r'^musicas/alteracao/(?P<music_id>\d+)/$', 'repertory.views.music_add', name='music_edit'),
	url(r'^musicas/(?P<music_id>\d+)/$', 'repertory.views.music_detail', name='music_detail'),
	url(r'^musicas/exclusao/(?P<music_id>\d+)/$', 'repertory.views.music_remove', name='music_remove'),
	url(r'^musicas/compartilhamento/(?P<music_id>\d+)/$', 'repertory.views.music_share', name='music_share'),
	url(r'^musicas/aprovacao/(?P<music_id>\d+)/$', 'repertory.views.music_approve', name='music_approve'),
	# Download de arquivo de música
	url(r'^musicas/download/(?P<music_id>\d+)/(?P<music_file_type>\d+)$', 'repertory.views.music_file_download', name='music_file_download'),
	# telas repertório
	url(r'^repertorios/$', 'repertory.views.repertories_list', name='repertories_list'),
	url(r'^repertorios/cadastro/$', 'repertory.views.repertory_add', name='repertory_add'),
	url(r'^repertorios/alteracao/(?P<repertory_id>\d+)/$', 'repertory.views.repertory_add', name='repertory_edit'),
	url(r'^repertorios/(?P<repertory_id>\d+)/$', 'repertory.views.repertory_detail', name='repertory_detail'),
	url(r'^repertorios/exclusao/(?P<repertory_id>\d+)/$', 'repertory.views.repertory_remove', name='repertory_remove'),
	# telas eventos
	url(r'^eventos/$', 'repertory.views.events_list', name='events_list'),
	url(r'^eventos/cadastro/$', 'repertory.views.event_add', name='event_add'),
	url(r'^eventos/alteracao/(?P<event_id>\d+)/$', 'repertory.views.event_add', name='event_edit'),
	url(r'^eventos/(?P<event_id>\d+)/$', 'repertory.views.event_detail', name='event_detail'),
	url(r'^eventos/exclusao/(?P<event_id>\d+)/$', 'repertory.views.event_remove', name='event_remove'),
	# notificações
	url(r'^notificacoes/$', 'repertory.views.notifications', name='notifications'),
	url(r'^notificacoes/quantidade/$', 'repertory.views.notifications_count', name='notifications_count'),
	# telas de login
	# Modulo pronto do django. Aqui utilizamos uma view do django que automaticamente
	# renderiza o template em "/registration/login.html"
	url(r'^conta/acesso/$', 'django.contrib.auth.views.login'),
	url(r'^conta/sair/$', 'django.contrib.auth.views.logout_then_login', name='sair'),
)