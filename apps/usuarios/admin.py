from django.contrib import admin
from django.utils.html import format_html

from .models import UsuarioORM, AdministradorORM, VendedorORM


# ---------- Base común ----------
class UsuarioBaseAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'activo_badge', 'fecha_creacion', 'rol_display',
    )
    list_filter = ('activo',)
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('uuid', 'fecha_creacion')
    list_per_page = 25

    @admin.display(description='Activo', ordering='activo')
    def activo_badge(self, obj):
        colores = {
            'activo':     ('#28a745', 'Activo'),
            'pendiente':  ('#ffc107', 'Pendiente'),
            'inactivo':   ('#dc3545', 'Inactivo'),
        }
        color, texto = colores.get(obj.activo, ('#6c757d', obj.activo))
        return format_html(
            '<span style="color:white;background:{};padding:2px 8px;'
            'border-radius:4px;">{}</span>',
            color, texto,
        )

    @admin.display(description='Rol')
    def rol_display(self, obj):
        return obj.rol.capitalize()


# ---------- Padre ----------
@admin.register(UsuarioORM)
class UsuarioORMAdmin(UsuarioBaseAdmin):
    fieldsets = (
        ('Identidad', {
            'fields': ('uuid', 'username', 'email', 'password')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',),
        }),
    )


# ---------- Hijo 1: Administrador ----------
@admin.register(AdministradorORM)
class AdministradorORMAdmin(UsuarioBaseAdmin):
    fieldsets = (
        ('Identidad', {
            'fields': ('uuid', 'username', 'email', 'password')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',),
        }),
    )


# ---------- Hijo 2: Vendedor ----------
@admin.register(VendedorORM)
class VendedorORMAdmin(UsuarioBaseAdmin):
    list_display = UsuarioBaseAdmin.list_display + ('admin',)
    list_filter = ('activo', 'admin')
    list_select_related = ('admin',)
    autocomplete_fields = ('admin',)   # buscador en vez de <select> gigante

    fieldsets = (
        ('Identidad', {
            'fields': ('uuid', 'username', 'email', 'password')
        }),
        ('Jerarquía', {
            'fields': ('admin',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',),
        }),
    )
