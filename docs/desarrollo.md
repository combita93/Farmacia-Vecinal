# Desarrollo

## Comandos de `uv`

```bash
uv sync                         # instala dependencias y actualiza uv.lock
uv run farmacia-vecinal         # inicia la aplicacion
uv run python -m farmacia_vecinal # inicia el modulo
uv run python -m compileall -q src # valida sintaxis
uv run python -m unittest discover -s tests -v # ejecuta pruebas de dominio
```

## Base de datos local

La base `database/farmacia.db` no se versiona. Para comenzar con datos limpios, detenga la aplicacion y elimine el archivo local; al iniciar de nuevo se recrearan la carpeta, las tablas y los usuarios de demostracion.

## Convenciones

- Codigo de aplicacion dentro de `src/farmacia_vecinal`.
- Documentacion funcional y tecnica dentro de `docs`.
- Cambios pequenos y enfocados.
- Errores de persistencia se capturan como `SQLAlchemyError` y se convierten en `DatabaseError`.
- La persistencia usa SQLAlchemy ORM; no se escriben sentencias SQL manuales en la aplicacion.
- Las dependencias de ejecucion se declaran en `pyproject.toml` y no se instalan manualmente con `pip`.
- La logica de negocio se prueba con `unittest` sin depender de una pantalla Qt.
