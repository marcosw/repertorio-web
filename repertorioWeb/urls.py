from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'repertorioWeb.views.home', name='home'),
    # url(r'^repertorioWeb/', include('repertorioWeb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # Aqui nos apontamos para o root URLconf no modulo repertory.urls. 
	# Utilizamos namespace devido ao grande numero de modulos que o sistema pode conter.
	url(r'^', include('repertory.urls', namespace="repertory")),
)
