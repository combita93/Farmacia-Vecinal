# Farmacia Vecinal

Aplicacion de escritorio para gestionar el inventario y la entrega de medicamentos de una farmacia comunal. Usa PySide6 para la interfaz, SQLAlchemy ORM y SQLite para guardar los datos localmente.

## Requisitos

- macOS, Linux o Windows
- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/)

## Instalacion

Desde la raiz del proyecto:

```bash
uv sync
```

`uv` crea el entorno virtual, instala PySide6 y genera `uv.lock` para reproducir las dependencias.

## Ejecucion

```bash
uv run farmacia-vecinal
```

Tambien puede ejecutarse como modulo:

```bash
uv run python -m farmacia_vecinal
```

La base de datos `database/farmacia.db` se crea automaticamente junto con la carpeta `database/`. Este archivo es local y esta excluido de Git.

## Usuarios iniciales

| Rol | Usuario | Contrasena |
| --- | --- | --- |
| Bodega | `juan` | `1234` |
| Entrega | `carlos` | `4567` |

Estas credenciales son datos de demostracion local. Deben cambiarse antes de usar el sistema en un entorno real.

## Uso

1. Inicia sesion con el rol correspondiente.
2. Usa **Ingreso a Bodega** para registrar unidades y laboratorio.
3. Selecciona una fila del inventario para entregar, editar o eliminar un medicamento.
4. Usa **Verificacion de medicamentos** para consultar stock bajo o vencimientos proximos.
5. Cierra la ventana para cerrar correctamente la conexion SQLite.

El rol `bodega` puede registrar, editar y eliminar. El rol `entrega` puede descontar unidades. Las alertas son visibles para cualquier usuario.

## Validacion

```bash
uv run python -m compileall -q src
uv run python -c "from farmacia_vecinal.database import FarmaciaDB; db = FarmaciaDB(); print('Base de datos disponible'); db.close()"
```

Para probar la interfaz en macOS o Linux se necesita una sesion grafica activa.

## Estructura

```text
src/farmacia_vecinal/
├── database.py       # Repositorio SQLite
├── models.py         # Modelos inmutables del dominio
├── services.py       # Casos de uso y validaciones
├── main.py           # Entrada publica
└── ui/               # Ventana, widgets y estilos Qt
	├── main_window.py
	└── styles.py
```

La documentacion tecnica esta en [`docs/`](docs/).

## Pruebas

```bash
uv run python -m unittest discover -s tests -v
```
