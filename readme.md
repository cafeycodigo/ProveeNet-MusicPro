# ProveeNet

Plataforma B2B para conectar empresas compradoras y proveedoras. El proyecto
contempla catálogos de productos, relaciones comerciales, conversaciones,
cotizaciones y órdenes de compra.

## Autoría y proyecto de origen

Desarrollado por [bemtorres](https://github.com/bemtorres) para
[Café y Código](https://cafeycodigo.org). Este proyecto nace de la idea de
[MusicPro Core](https://github.com/cafeycodigo/musicpro-core), cuya
[aplicación de referencia](https://cafeycodigo.github.io/musicpro-core/) presenta
el proyecto MusicPro. ProveeNet desarrolla la parte orientada al docente dentro
de esa propuesta.

![Vista conceptual de ProveeNet](simulations.png)

Actualmente cuenta con la base del backend en Django: 29 modelos, migraciones
y datos de ejemplo organizados por aplicación. La página principal pública permite buscar proveedores por empresa o producto, país
y categoría. La API y las funciones en tiempo real están pendientes de implementación.

## Inicio rápido

Desde la raíz del proyecto, en PowerShell, con Python 3.13:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

El servidor local queda disponible en `http://127.0.0.1:8000/`.
La página principal está en `/` y el administrador en `/admin/`.
Actualmente no hay cuentas de administrador en la base local. Los usuarios
`demo_comprador` y `demo_proveedor` son cuentas normales y no pueden entrar al admin.

Para crear tu administrador, ejecuta:

```powershell
python manage.py createsuperuser --username admin --email admin@example.com
```

El comando solicita la contraseña de forma interactiva. Después podrás entrar en
`http://127.0.0.1:8000/admin/` con el usuario `admin` y la contraseña que hayas elegido.
El seeder no crea administradores ni asigna permisos de administración.

## Organización

| Aplicación | Contenido |
|---|---|
| `app` | Parte pública |
| `accounts` | Usuarios y autenticación |
| `companies` | Empresas, países y miembros |
| `catalog` | Productos, categorías y ofertas |
| `social` | Favoritos, seguimientos y publicaciones |
| `messaging` | Conversaciones y mensajes |
| `quotations` | Solicitudes, cotizaciones y órdenes de compra |
| `collaboration` | Sesiones de catálogo y llamadas |
| `notifications` | Notificaciones e historial |

## Datos de ejemplo y pruebas

```powershell
python manage.py seed
python manage.py test accounts companies catalog social messaging quotations collaboration notifications app
```

El seeder puede repetirse sin duplicar registros. Los usuarios de demostración nuevos o sin contraseña reciben `ProveeNet2026!`.
Las contraseñas existentes se conservan. Los comandos individuales y los detalles
de instalación están en las especificaciones técnicas.

## Documentación

- [Especificación funcional y propuesta original](_docs/especificacion-funcional.md)
- [Especificaciones técnicas del proyecto](_docs/especificaciones-tecnicas.md)

La carga masiva incluye 100 usuarios ficticios de diez nacionalidades, 20 empresas
y más de 200 productos. Reutiliza los diez retratos WebP y los logos locales.
Ver [imágenes de demostración](_docs/imagenes-demo.md).


Para entrar con datos de ejemplo: usuario `demo_comprador` o `demo_proveedor`,
contraseña inicial `ProveeNet2026!` (solo desarrollo).

```powershell
python manage.py seed --scale 2
python manage.py seed --password "MiDemo2026!" --reset-passwords
```

`--scale` acepta valores de 1 a 10. El restablecimiento afecta únicamente a las
cuentas demo del seeder; no crea permisos de administrador.
Ver [volúmenes, credenciales y reglas de simulación](_docs/datos-simulados.md).

## Estilos de la página principal

La interfaz de `app` usa Tailwind CSS compilado localmente. El archivo generado
`app/static/app/css/site.css` está incluido: Django puede servir la página sin Node.
Para modificar los estilos o añadir clases en las plantillas:

```powershell
npm ci
npm run build:css
# Durante el desarrollo:
npm run watch:css
```

Los estilos fuente están en `app/static/app/css/input.css`; la plantilla principal,
en `app/templates/app/home.html`. Los filtros se procesan en el servidor y funcionan
sin JavaScript. El directorio muestra proveedores activos; `Ver productos` despliega
sus productos activos. Las fuentes web tienen alternativas locales.

El catálogo demo reutiliza [20 imágenes genéricas WebP](_docs/imagenes-productos.md),
dos por categoría, para ilustrar los productos sin depender de servicios externos.

El buscador permite elegir alcance global, local o internacional respecto al campo
`Tu país`. El país de referencia predeterminado es Chile cuando existe en el catálogo;
si no hay un país válido seleccionado, la búsqueda usa alcance global. Las cifras de
países y proveedores corresponden a empresas activas registradas, no a cobertura prometida.

## Presentación del proyecto

Abre `/app/presentacion` para ver las once diapositivas del proyecto. Incluye
navegación con flechas, selector, pantalla completa, impresión a PDF y descarga
del PPTX editable en `entregables/ProveeNet-presentacion.pptx`. El contenido web
se mantiene en `app/presentation_data.json`. Las funciones previstas se distinguen
de las que ya están implementadas.

## Acceso y espacio de trabajo

`/login` inicia sesión con el usuario integrado de Django y redirige a `/home`.
El inicio usa el diseño de `simulations.png`: encabezado claro, sidebar azul oscuro
y controles índigo. Cada sección del sidebar abre un listado o una ficha real.

- Administrador de plataforma: usuario `is_superuser`, resumen global de empresas,
  usuarios, catálogo, categorías y cotizaciones. Acceso a la administración avanzada.
- Comprador: solicitudes y cotizaciones de la empresa activa, pedidos y favoritos.
- Proveedor: catálogo propio, solicitudes recibidas, cotizaciones y pedidos.
- Administrador de empresa: añade el acceso a los miembros de su empresa.
- Usuario sin empresa: exploración pública, favoritos y notificaciones personales.

El selector de espacio valida las membresías activas. Una empresa compradora y
proveedora puede cambiar de vista. Los usuarios normales nunca eligen un rol libre:
la aplicación lo resuelve a partir de su membresía y del tipo de empresa. El
administrador de plataforma puede consultar espacios empresariales desde el selector.
Las conversaciones de miembros no administradores requieren participación, además
de pertenecer a una empresa de la conversación. Las notificaciones son personales.

Para crear un administrador local con contraseña aleatoria:

```powershell
python manage.py create_platform_admin
```

El comando muestra la contraseña inicial una vez y conserva cuentas existentes.
También puedes usar `createsuperuser` y gestionar su contraseña con `changepassword`.
El cierre de sesión y el cambio de contexto usan POST con CSRF. El catálogo del
proveedor permite crear, editar y eliminar productos desde sus rutas específicas.
Los listados de mensajes, reuniones y cotizaciones son vistas de consulta; sus
operaciones se habilitarán cuando se completen esos módulos.

### Modal de accesos de demostración

En desarrollo, `/login` incluye **Accesos de demostración**. El modal centrado
permite elegir una cuenta ficticia y completar el formulario sin iniciar sesión
hasta pulsar el botón de acceso. Se acepta usuario o correo único, sin distinguir
mayúsculas en el correo. Para completar las cuentas del selector:

```powershell
python manage.py seed
python manage.py seed_demo_access
```

La contraseña demo procede de `SEED_DEMO_PASSWORD` o de la clave demo del seeder.
El selector solo incluye cuentas demo activas cuya contraseña coincida. No cambia
contraseñas existentes ni publica el acceso de `admin_proveenet`. Si `DEBUG=False`
o `DEMO_LOGIN_ENABLED=False`, el modal y sus credenciales no se envían al navegador.

### Rutas explícitas para estudiar el panel

Cada pantalla tiene su propia ruta y función en `app/urls.py` y `app/dashboard.py`.
Por ejemplo, `/home/productos` llama a `productos(request)` y tiene el nombre
`app:dashboard_productos`; `/home/mensajes` llama a `mensajes(request)` y tiene
el nombre `app:dashboard_mensajes`. No hay una ruta que capture cualquier sección.

Las funciones de cada pantalla están protegidas con `login_required`. Comparten
el auxiliar privado `_render_dashboard` para preparar el diseño y aplicar los
permisos, sin repetir esas reglas en cada vista. `SECTION_URL_NAMES` contiene los
nombres explícitos que usan el menú y las tarjetas para enlazar las pantallas.

### CRUD didáctico del equipo

`/home/equipo` permite listar, agregar, editar y quitar miembros de la empresa
activa. Usa formularios HTML y `request.POST`, sin Django Forms ni ModelForm.
El código está en `companies/team_views.py`, con rutas explícitas en `app/urls.py`
y una plantilla por operación. El [recorrido para estudiantes](_docs/crud-equipo.md)
explica cada paso y sus validaciones. Quitar un miembro conserva su usuario.

### CRUD didáctico del catálogo

En `/home/catalogo`, el proveedor puede administrar sus productos. El listado y
las operaciones de crear, editar y eliminar tienen rutas propias en `app/urls.py`.
Las vistas están en `catalog/views.py` y el formulario que valida los datos en
`catalog/forms.py`. Cada operación usa la empresa activa para limitar qué productos
puede modificar el usuario; eliminar requiere confirmación y no permite borrar
productos que tengan información relacionada.
