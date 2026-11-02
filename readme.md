# ProveeNet

Plataforma B2B para conectar empresas compradoras y proveedoras. El proyecto
contempla catálogos de productos, relaciones comerciales, conversaciones,
cotizaciones y órdenes de compra.

![Vista conceptual de ProveeNet](simulations.png)

Actualmente cuenta con la base del backend en Django: 29 modelos, migraciones
y datos de ejemplo organizados por aplicación. La interfaz pública, la API y
las funciones en tiempo real están pendientes de implementación.

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
Por ahora, la única ruta configurada es `/admin/`; la página de inicio aún
no está implementada. Para acceder al administrador, crea una cuenta:

```powershell
python manage.py createsuperuser
```

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

El seeder puede repetirse sin duplicar registros. Los usuarios de demostración
se crean sin contraseña utilizable. Los comandos individuales y los detalles
de instalación están en las especificaciones técnicas.

## Documentación

- [Especificación funcional y propuesta original](_docs/especificacion-funcional.md)
- [Especificaciones técnicas del proyecto](_docs/especificaciones-tecnicas.md)
