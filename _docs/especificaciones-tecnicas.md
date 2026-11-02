# Especificaciones técnicas de ProveeNet

Este documento describe el código actual y separa lo implementado de la
arquitectura propuesta en la [especificación funcional](especificacion-funcional.md).

## 1. Estado de implementación

Implementado: proyecto Django, separación por dominios, usuario personalizado,
29 modelos, migraciones iniciales por aplicación, seeders y pruebas de integridad.
`app` está reservada para la parte pública y no tiene modelos.

Pendiente: páginas públicas, API, permisos por empresa, servicios comerciales,
chat en tiempo real, sincronización de catálogo, llamadas y despliegue.
Las entidades de estos módulos existen, pero sus flujos todavía no son ejecutables.

## 2. Entorno y dependencias

Entorno local comprobado: Python 3.13.5 y SQLite. Las versiones del entorno
están fijadas en [`requirements.txt`](../requirements.txt):

| Paquete | Versión |
|---|---|
| Django | 6.1.2 |
| asgiref | 3.13.0 |
| sqlparse | 0.6.1 |
| tzdata | 2026.6 |

No se han incorporado Django REST Framework, Channels, Redis, Celery ni un
controlador PostgreSQL. Next.js, WebRTC y almacenamiento S3 pertenecen a la
propuesta funcional y no forman parte del código actual.

## 3. Estructura y responsabilidades

| Directorio | Responsabilidad | Modelos |
|---|---|---|
| `core` | Configuración, rutas, WSGI/ASGI y ejecución de seeders | — |
| `app` | Parte pública; vistas y páginas de entrada por desarrollar | — |
| `accounts` | Autenticación Django | Usuario |
| `companies` | Identidad empresarial y membresías | Pais, Empresa, UsuarioEmpresa |
| `catalog` | Catálogo y promociones | Categoria, Producto, ProductoImagen, Oferta |
| `social` | Red comercial | Favorito, SeguimientoProveedor, Publicacion |
| `messaging` | Historial de conversaciones entre empresas | Conversacion, ParticipanteConversacion, Mensaje, ProductoCompartido, EventoConversacion |
| `quotations` | Solicitudes, versiones y compra | SolicitudCotizacion, SolicitudDetalle, SolicitudProveedor, Cotizacion, CotizacionDetalle, OrdenCompra |
| `collaboration` | Metadatos de colaboración y llamadas | SesionCatalogo, ParticipanteSesionCatalogo, EventoCatalogo, Llamada, ParticipanteLlamada |
| `notifications` | Avisos y trazabilidad | Notificacion, HistorialEstado |

Los modelos usan referencias entre aplicaciones y tablas con nombres en español.
Cada dominio con modelos tiene su directorio `migrations`, su archivo `seeders.py`
y un comando `management/commands/seed_<aplicación>.py`.

## 4. Persistencia e integridad

La configuración actual usa `db.sqlite3` en la raíz. Las claves primarias de
las entidades son `BigAutoField`, los importes usan `DecimalField` con 18 dígitos
y dos decimales, y las cantidades comerciales usan tres decimales.
Las fechas se manejan con `USE_TZ = True` y `TIME_ZONE = "UTC"`.

Las relaciones obligatorias usan `PROTECT`; las opcionales usan `SET_NULL`.
Las claves foráneas conservan columnas `id_*` mediante `db_column`.

Restricciones implementadas en la base:

- Unicidad de membresías, favoritos, seguimientos y participantes por relación.
- SKU único por empresa; slug único de categoría; código ISO de país único.
- Una invitación por solicitud y proveedor; número de versión único por invitación.
- Una orden por cotización y número de orden único.
- Stock y precios de referencia no negativos; precio y moneda informados juntos.
- Ofertas con precio no negativo y fecha final posterior al inicio.
- Cantidades positivas, versiones positivas e importes de cotización no negativos.
- Empresas compradora y proveedora distintas dentro de una conversación.

El detalle de campos se encuentra en los `models.py` de cada dominio y en el
[diccionario funcional](especificacion-funcional.md#8-diccionario-de-datos-completo).
No todas las reglas comerciales del diccionario están implementadas como validaciones.

## 5. Autenticación, rutas y configuración

`AUTH_USER_MODEL = "accounts.Usuario"`. El modelo hereda de `AbstractUser`,
conserva `username`, grupos y permisos, y exige correo electrónico único.
Los campos de Django `first_name`, `last_name`, `password`, `is_active` y
`date_joined` se almacenan en las columnas `nombre`, `apellido`, `password_hash`,
`activo` y `fecha_registro`. Las contraseñas se gestionan con los métodos de Django.

`core/urls.py` expone únicamente `/admin/`. Los modelos de negocio todavía no
están registrados en el administrador y no hay endpoints API.
Las vistas de dominio y la parte pública siguen siendo esqueletos de aplicación.

La configuración es de desarrollo: `DEBUG = True`, `ALLOWED_HOSTS = []`,
idioma `en-us`, estáticos en `static/` y backend de correo por consola.
Antes de desplegar se deben externalizar la clave secreta y las credenciales,
configurar hosts, desactivar depuración y definir servicios de almacenamiento.

## 6. Instalación y migraciones

Desde la raíz, en PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Las ocho aplicaciones con modelos tienen migración `0001_initial`.
`app` no requiere migración mientras no tenga modelos.
Tras modificar los modelos:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

## 7. Seeders

`core/seeding.py` ejecuta los seeders en una transacción y resuelve sus
prerrequisitos. Cada módulo expone `seed(context)`, que devuelve referencias
para los módulos dependientes. Cada dependencia se ejecuta una vez por carga.

| Comando | Prerrequisito directo |
|---|---|
| `python manage.py seed_accounts` | Ninguno |
| `python manage.py seed_companies` | accounts |
| `python manage.py seed_catalog` | companies |
| `python manage.py seed_social` | catalog |
| `python manage.py seed_messaging` | catalog |
| `python manage.py seed_quotations` | catalog |
| `python manage.py seed_collaboration` | messaging |
| `python manage.py seed_notifications` | quotations |

`python manage.py seed` carga todos los dominios. Los comandos individuales
cargan sus dependencias de forma transitiva. Se utilizan búsquedas con
`get_or_create` para conservar los registros existentes y evitar duplicados
cuando se repiten las cargas con sus claves de búsqueda originales.

Los datos ficticios incluyen una compradora chilena y una proveedora alemana,
un osciloscopio X200, conversaciones, colaboración, una cotización y una orden.
Los usuarios `demo_comprador` y `demo_proveedor` se crean sin contraseña utilizable.
Para habilitar el acceso de uno de ellos:

```powershell
python manage.py changepassword demo_comprador
```

## 8. Verificación

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test accounts companies catalog social messaging quotations collaboration notifications app
python -m pip check
```

Las cuatro pruebas en `companies/tests.py` verifican:

- Carga global repetible, conservación de datos editados y validación de registros.
- Rechazo de stock negativo y membresías duplicadas por la base.
- Rechazo de conversaciones con la misma empresa en ambos extremos.
- Ejecución de cada seeder desde una base vacía y repetición sin duplicados.

## 9. Trabajo técnico pendiente

La capa de servicios/API debe validar pertenencia y rol en la empresa activa,
acceso a conversaciones, consentimiento para colaboración, correspondencia de
los detalles con su solicitud e inmutabilidad de las cotizaciones enviadas.
También debe definir estados permitidos y sus transiciones, política de ofertas
superpuestas y reglas de cálculo de impuestos, envío y totales.

La especificación original propone PostgreSQL, REST, WebSockets y WebRTC.
Su incorporación requiere dependencias, configuración, servicios y pruebas
adicionales; la existencia de modelos no implementa esos servicios.
