# -*-encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class City(models.Model):
	name = models.CharField(max_length=200)
	federative_unit = models.CharField(max_length=10)
	# Com unique_together, fazemos com que o banco não permita cadastrar dois nomes iguais
	
	class Meta:
		ordering = ['name']
		unique_together = ('name', 'federative_unit')

	# Damos um nome ao objeto para quando ele for chamado
	def __unicode__(self):
		return self.name

class Location(models.Model):
	name = models.CharField(max_length=200)
	adress = models.CharField(max_length=500)
	city = models.ForeignKey(City, on_delete=models.PROTECT)
	
	class Meta:
		ordering = ['name']
		unique_together = ('name', 'adress', 'city')
		
	def __unicode__(self):
		return self.name + " - " + self.city.name

class EventType(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	class Meta:
		ordering = ['name']
	
	def __unicode__(self):
		return self.name

class Event(models.Model):
	user = models.ForeignKey(User)
	location = models.ForeignKey(Location, on_delete=models.PROTECT)
	eventType = models.ForeignKey(EventType, on_delete=models.PROTECT)
	date = models.DateTimeField('data de início')
	observation = models.CharField(max_length=200, blank=True)
	
	def __unicode__(self):
		return self.eventType.name + " - " +  self.location.name + " - " + str(self.date)

class Author(models.Model):
	completeName = models.CharField(max_length=200, unique=True)
	
	class Meta:
		ordering = ['completeName']
	
	def __unicode__(self):
		return self.completeName

class MusicCathegory(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	class Meta:
		ordering = ['name']
	
	def __unicode__(self):
		return self.name

class LiturgicalTime(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	class Meta:
		ordering = ['name']
	
	def __unicode__(self):
		return self.name

class LiturgicalYear(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	class Meta:
		ordering = ['name']
	
	def __unicode__(self):
		return self.name

class Music(models.Model):
	user = models.ForeignKey(User)
	# Uma música pode estar relacionada a outra música.
	musicReference = models.ForeignKey('self', null=True, blank=True)
	author = models.ForeignKey(Author, on_delete=models.PROTECT)
	musicCathegories = models.ManyToManyField(MusicCathegory, through='Music_musicCathegory', null=True)
	liturgicalTimes = models.ManyToManyField(LiturgicalTime, through='Music_liturgicalTime', null=True)
	liturgicalYears = models.ManyToManyField(LiturgicalYear, through='Music_liturgicalYear', null=True)
	name = models.CharField(max_length=200, verbose_name = 'Nome')
	firstPhrase = models.CharField(max_length=200)
	tone = models.CharField(max_length=5, verbose_name = 'Tom')
	# Em MEDIA_ROOT (settings.py) devemos adicionar o repositório principal para upload
	cipherFile = models.FileField(upload_to='cipherfiles')
	#blank indica que o campo pode ser deixado em branco
	scoreFile = models.FileField(upload_to='scorefiles', blank=True)
	tabFile = models.FileField(upload_to='tabfiles', blank=True)
	audioFile = models.FileField(upload_to='audiofiles')
	shared = models.BooleanField(default=False)
	sentForApproval = models.BooleanField()

	class Meta:
		ordering = ['name']
		unique_together = ('name', 'tone')
		verbose_name = 'Musica'
		permissions = (
			("approve_music", "Can approve musics"),
		)
	
	# Reescrevemos o método save para que ele delete arquivos antigos quando substituido
	# ao atualizar o objeto
	def save(self, *args, **kwargs):
		try:
			this = Music.objects.get(id=self.id)
			# save=false só removerá o objeto File quando o modelo é salvo
			if this.cipherFile != self.cipherFile:
				this.cipherFile.delete(save=False)
			if this.scoreFile != self.scoreFile:
				this.scoreFile.delete(save=False)
			if this.tabFile != self.tabFile:
				this.tabFile.delete(save=False)
			if this.audioFile != self.audioFile:
				this.audioFile.delete(save=False)
		except: pass # Quando um novo objeto é criado, nada é feito
		super(Music, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.name + " - " + self.tone + " - "+ self.author.completeName

#Criação de tabela associativa manualmente
class Music_musicCathegory(models.Model):
	music = models.ForeignKey(Music, on_delete=models.CASCADE)
	musicCathegory = models.ForeignKey(MusicCathegory, on_delete=models.PROTECT)

#Criação de tabela associativa manualmente
class Music_liturgicalTime(models.Model):
	music = models.ForeignKey(Music, on_delete=models.CASCADE)
	liturgicalTime = models.ForeignKey(LiturgicalTime, on_delete=models.PROTECT)

#Criação de tabela associativa manualmente
class Music_liturgicalYear(models.Model):
	music = models.ForeignKey(Music, on_delete=models.CASCADE)
	liturgicalYear = models.ForeignKey(LiturgicalYear, on_delete=models.PROTECT)

class Repertory(models.Model):
	user = models.ForeignKey(User, related_name='repertory_user')
	involved = models.ManyToManyField(User, related_name='repertory_involved', through='Repertory_involved', null=True)
	musics = models.ManyToManyField(Music, through='Repertory_music', null=True)
	event = models.ForeignKey(Event, on_delete=models.PROTECT)
	sentForApproval = models.BooleanField(default=False)
	# Caso approved seja falso, o repertório está suspenso, caso seja true, está aprovado.
	approved = models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.event

#Criação de tabela associativa manualmente
class Repertory_involved(models.Model):
	repertory = models.ForeignKey(Repertory, on_delete=models.CASCADE)
	#Verificar se está correto este related_name
	user = models.ForeignKey(User, related_name='repertory_involved_user', on_delete=models.PROTECT)

#Criação de tabela associativa manualmente
class Repertory_music(models.Model):
	repertory = models.ForeignKey(Repertory, on_delete=models.CASCADE)
	music = models.ForeignKey(Music, on_delete=models.PROTECT)
	
class Notification(models.Model):
	music = models.ForeignKey(Music, null=True, on_delete=models.CASCADE)
	repertory = models.ForeignKey(Repertory, null=True, on_delete=models.CASCADE)
	# Utilizamos receiver para saber para quem a notificação será exibida 
	receiver = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
	systemMessage = models.CharField(max_length=1024, null=True)
	userMessage = models.CharField(max_length=1024, null=True)
	seen = models.BooleanField(default=False)
	# adiciona a data atual automaticamente
	date = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-date']
	