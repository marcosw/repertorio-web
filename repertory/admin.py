from django.contrib import admin
from repertory.models import Repertory
from repertory.models import Event
from repertory.models import City
from repertory.models import Location
from repertory.models import EventType
from repertory.models import Music
from repertory.models import Author
from repertory.models import MusicCathegory
from repertory.models import LiturgicalTime
from repertory.models import LiturgicalYear


# class MusicCathegoryInline(admin.TabularInline):
# 	model = Music.musicCathegories.through
# 	extra = 3

class MusicAdmin(admin.ModelAdmin):
	# fieldsets = [
	# 	(None,{'fields':['question']}),
	# 	('Date information',{'fields':['pub_date'],'classes':['collapse']}),
	# ]
	# inlines = [MusicCathegoryInline]
	list_display = ('name', 'tone')
	# list_filter = ['pub_date']
	# search_fields = ['question']
	# date_hierarchy = 'pub_date'

admin.site.register(Repertory)
admin.site.register(Event)
admin.site.register(City)
admin.site.register(Location)
admin.site.register(EventType)
admin.site.register(Music, MusicAdmin)
admin.site.register(Author)
admin.site.register(MusicCathegory)
admin.site.register(LiturgicalTime)
admin.site.register(LiturgicalYear)