from django.contrib import admin

from appturopamiestilo.models import ModuloPerfil, Perfil, Modulo, AccesoModulo, PerfilPersona, Pais, Provincia, Canton, \
    Parroquia, Persona, Sexo, TipoIdentificacion, Nacionalidad, SectorComercial, ActividadComercial, TipoSangre, Sector, \
    NivelAcademico, EstadoCivil

# Register your models here.

admin.site.register(ModuloPerfil)
admin.site.register(Perfil)
admin.site.register(Modulo)
admin.site.register(AccesoModulo)
admin.site.register(PerfilPersona)
admin.site.register(Pais)
admin.site.register(Provincia)
admin.site.register(Canton)
admin.site.register(Parroquia)
admin.site.register(Persona)
admin.site.register(Sexo)
admin.site.register(TipoIdentificacion)
admin.site.register(Nacionalidad)
admin.site.register(SectorComercial)
admin.site.register(ActividadComercial)
admin.site.register(TipoSangre)
admin.site.register(Sector)
admin.site.register(NivelAcademico)
admin.site.register(EstadoCivil)