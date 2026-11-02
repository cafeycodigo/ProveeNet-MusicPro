# Datos simulados y acceso demo

## Carga

Después de aplicar las migraciones:

```powershell
python manage.py migrate
python manage.py seed
```

Los seeders anteriores incluían principalmente un ejemplo por modelo. Ahora cada
aplicación conserva ese escenario y añade datos masivos con referencias coherentes.
La carga completa es transaccional y no borra registros. Las claves de búsqueda
estables evitan duplicados al repetir el mismo volumen. Al finalizar, el comando
muestra los totales de la base por modelo, incluyendo registros previos.

## Usuarios y contraseñas

- Usuarios principales: `demo_comprador`, `demo_proveedor`.
- Otros perfiles: `demo_sofia`, `demo_mateo`, `demo_aiko`, `demo_arjun`,
  `demo_amina`, `demo_claire`, `demo_omar`, `demo_jiwoo`.
- Cuentas adicionales: `demo_usuario_0011` a `demo_usuario_0100`.
- Contraseña inicial de desarrollo: `ProveeNet2026!`.

Las cuentas nuevas y las cuentas demo con contraseña inutilizable reciben un
hash de Django para esta contraseña. Las contraseñas personalizadas se conservan.
Los usuarios son cuentas normales, sin permisos de administrador. Los diez
retratos locales se reutilizan entre los cien perfiles.

Para elegir otra contraseña y reasignarla a las cuentas demo del volumen elegido:

```powershell
python manage.py seed --password "MiDemo2026!" --reset-passwords
```

También puede definirse `SEED_DEMO_PASSWORD` en el entorno. La contraseña no se
imprime en el reporte de carga. `--reset-passwords` solo afecta a las cuentas
identificadas por el seeder y no modifica otras cuentas del sistema.

## Volumen predeterminado

Totales esperados sobre una base migrada vacía, con `--scale 1`:

| Modelo | Registros |
|---|---:|
| User (autenticación Django) | 100 |
| PerfilUsuario | 100 |
| Pais | 10 |
| Empresa | 20 |
| UsuarioEmpresa | 190 |
| Categoria | 11 |
| Producto | 201 |
| ProductoImagen | 401 |
| Oferta | 101 |
| Favorito | 501 |
| SeguimientoProveedor | 120 |
| Publicacion | 51 |
| Conversacion | 41 |
| ParticipanteConversacion | 180 |
| Mensaje | 801 |
| ProductoCompartido | 81 |
| EventoConversacion | 81 |
| SolicitudCotizacion | 31 |
| SolicitudDetalle | 91 |
| SolicitudProveedor | 91 |
| Cotizacion | 181 |
| CotizacionDetalle | 541 |
| OrdenCompra | 11 |
| SesionCatalogo | 41 |
| ParticipanteSesionCatalogo | 180 |
| EventoCatalogo | 119 |
| Llamada | 81 |
| ParticipanteLlamada | 260 |
| Notificacion | 501 |
| HistorialEstado | 191 |

## Más volumen o carga individual

```powershell
python manage.py seed --scale 2
python manage.py seed_catalog --scale 2
python manage.py seed_messaging --scale 2
```

`--scale` acepta enteros de 1 a 10. Multiplica usuarios, empresas y escenarios;
los catálogos fijos y el ejemplo original no se multiplican. Los comandos por
aplicación cargan sus dependencias automáticamente. Reducir la escala no elimina
filas: los totales pueden superar la tabla si ya hubo una carga mayor. Ejecutar
`seed` completo con la misma escala permite completar todos los dominios.

## Escenarios y coherencia

- Diez países, empresas compradoras y proveedoras, roles y membresías activas.
- Categorías con jerarquía, productos con y sin stock, ofertas vigentes y vencidas.
- Favoritos, seguimientos y publicaciones publicadas o en borrador.
- Conversaciones con mensajes de miembros de ambas empresas, lectura y productos compartidos.
- Solicitudes multítem enviadas a tres proveedores, con dos versiones de cotización.
- Importes en EUR con aritmética decimal: suma de líneas, impuestos y envío.
- Órdenes de compra solo para cotizaciones aceptadas, conservando total y moneda.
- Sesiones pendientes o finalizadas con consentimiento, y llamadas de voz y video.
- Notificaciones leídas y pendientes e historial vinculado a cotizaciones y órdenes.

Las imágenes de producto usan veinte archivos WebP locales, dos por categoría,
reutilizados entre todos los productos demo. Las portadas alternan por proveedor
y serie, y la segunda imagen usa la otra variante de la categoría. Son imágenes
genéricas de demostración, no fotografías de los modelos comerciales indicados.
El osciloscopio del ejemplo inicial reutiliza la imagen del instrumento de medición.
Los placeholders originales bajo `example.com` se sustituyen al ejecutar el seeder;
las imágenes personalizadas se conservan. Ver [inventario y prompts](imagenes-productos.md).
La simulación no ejecuta llamadas, envíos de correo, WebSockets ni transacciones reales.

Las pruebas verifican repetibilidad, conservación de personalizaciones,
contraseñas, integridad de importes y pertenencia de remitentes a sus empresas.

Las empresas usan doce identidades visuales relacionadas con sus nombres,
compartidas únicamente entre variantes de la misma marca. Ver [logos de empresas](logos-empresas.md).
