# CRUD de equipo sin Django Forms

El ejemplo administra `UsuarioEmpresa`, la relación entre una cuenta de Django
y una empresa. Crear un miembro significa agregar esa relación. El usuario ya
debe existir. Eliminar un miembro quita la relación y conserva su cuenta.

## Dónde leer el código

1. `app/urls.py` declara las cuatro rutas explícitas.
2. `companies/team_views.py` contiene las cuatro vistas con comentarios CRUD.
3. `companies/models.py` define `UsuarioEmpresa`.
4. `app/templates/app/portal/equipo/` contiene una plantilla por operación.

| Operación | Ruta | Vista | Plantilla |
|---|---|---|---|
| Listar | `/home/equipo` | `equipo` | `listar.html` |
| Crear | `/home/equipo/nuevo` | `equipo_crear` | `crear.html` |
| Editar | `/home/equipo/<id>/editar` | `equipo_editar` | `editar.html` |
| Eliminar | `/home/equipo/<id>/eliminar` | `equipo_eliminar` | `eliminar.html` |

## El patrón básico

Las plantillas usan elementos HTML `<form>`, `<input>` y `<select>`. No usan
`django.forms`, `Form` ni `ModelForm`. Un formulario HTML sí es necesario para
enviar los datos del navegador mediante POST.

Una vista de creación sigue estos pasos:

```python
if request.method == "POST":
    rol = request.POST.get("rol", "")
    activo = request.POST.get("activo") == "on"
    # Validar los valores y buscar la cuenta existente.
    # UsuarioEmpresa.objects.create(...) guarda la nueva membresía.
    # redirect(...) vuelve al listado después de guardar.
```

La vista real valida el rol y la cuenta antes de guardar. Cuando encuentra un
error, vuelve a mostrar la misma plantilla con los valores enviados y los errores.
Después de guardar, redirige al listado para evitar repetir el POST al actualizar.

Para editar, `get_object_or_404` busca el registro dentro de la empresa activa,
se asignan los valores y `save()` guarda los cambios. Para eliminar, un GET
muestra la confirmación y un POST ejecuta `delete()`.

## Permisos y comprobaciones del ejemplo

- `login_required` exige una sesión.
- `_contexto_equipo` exige administrar la empresa activa.
- Cada consulta de membresía filtra por esa empresa, también al editar o quitar.
- `{% csrf_token %}` protege cada POST.
- El rol solo puede ser `administrador` o `ejecutivo` y no cambia los permisos
  globales del usuario.
- Una cuenta no puede repetirse en el mismo equipo.
- No se puede quitar ni desactivar al último administrador activo.
- Una persona no puede quitarse ni cambiar su propio rol o estado en esta pantalla.

Las pruebas están en `companies/test_team_crud.py`:

```powershell
python manage.py test companies.test_team_crud
```
