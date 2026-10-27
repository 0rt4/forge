# Forge

Forge es un gestor local de proyectos para desarrolladores, escrito en Python. Permite registrar proyectos en una base de datos SQLite y consultarlos desde una CLI sencilla. Los datos permanecen en el equipo local; Forge no sincroniza información con servicios externos.

## Requisitos

- Python 3.10 o posterior.
- No hay dependencias de ejecución externas: la CLI, SQLite y las pruebas usan la biblioteca estándar de Python.

## Instalación y ejecución

Para ejecutar desde una copia del repositorio sin instalar el paquete:

```bash
PYTHONPATH=src python -m forge --help
```

Para instalar el comando `forge` en el entorno activo:

```bash
python -m pip install .
forge --help
```

La instalación usa setuptools como backend de empaquetado. También se puede anteponer `PYTHONPATH=src` a `python -m forge` para ejecutar directamente desde el código fuente.

## Base de datos

Por defecto, Forge guarda SQLite en `$XDG_DATA_HOME/forge/forge.db` cuando `XDG_DATA_HOME` está definido; en caso contrario, usa `~/.local/share/forge/forge.db`. Crea la carpeta y la base automáticamente al ejecutar cualquier comando.

Se puede seleccionar otra base con `--db`. La opción global debe ir antes del subcomando:

```bash
python -m forge --db /tmp/forge.db init
```

Cada proyecto tiene un identificador asignado por SQLite, un nombre, una ruta opcional y una descripción opcional. El nombre es obligatorio: Forge elimina espacios al principio y al final, y rechaza nombres vacíos o compuestos solo por espacios. Se permiten nombres repetidos, pero la misma cadena de ruta no puede asignarse a más de un proyecto, incluidos los archivados. Forge conserva la ruta tal como se proporciona; no comprueba si el directorio existe ni normaliza rutas equivalentes.

## Funciones y comandos disponibles

### Inicializar la base

```bash
forge init
```

Crea la tabla de proyectos si aún no existe. Se puede ejecutar más de una vez.

### Añadir un proyecto

```bash
forge add "Mi proyecto" --path ~/code/mi-proyecto --description "Aplicación de ejemplo"
```

El nombre es obligatorio; `--path` y `--description` son opcionales. Forge muestra el ID asignado al guardar el proyecto. Si el nombre está vacío o contiene solo espacios, informa el error y termina con código `2`.

### Listar proyectos

```bash
forge list
```

Muestra los proyectos activos en orden de ID, con ID, nombre y ruta. Si no hay proyectos, muestra `No projects found.`. Para incluir proyectos archivados:

```bash
forge list --all
```

Las filas archivadas llevan la marca `archived`.

### Buscar proyectos

```bash
forge search forge
```

Busca coincidencias parciales sin distinguir mayúsculas y minúsculas en el nombre y la ruta. Por defecto excluye proyectos archivados; usa `--all` para incluirlos.

### Consultar un proyecto

```bash
forge show 1
```

Muestra ID, nombre, ruta y descripción. Si el ID no existe, informa el error por stderr y termina con código de salida `1`.

### Editar un proyecto

```bash
forge edit 1 --name "Nombre actualizado" --description "Descripción nueva"
```

Se puede cambiar cualquier combinación de `--name`, `--path` y `--description`; los campos omitidos no cambian. Es obligatorio indicar al menos una opción. Al cambiar el nombre se aplican las mismas reglas que al crear un proyecto. Un ID inexistente produce un error y código de salida `1`.

### Archivar y restaurar

```bash
forge archive 1
forge restore 1
```

Archivar conserva el proyecto en SQLite y lo excluye de `forge list`; `forge list --all` permite consultarlo. Restaurar vuelve a incluirlo en el listado normal. Repetir cualquiera de estas operaciones es seguro; si el ID no existe, Forge informa el error y termina con código `1`.

Al inicializar una base anterior que no tenga el campo de archivo, Forge lo añade sin eliminar los proyectos existentes.

Todos los comandos admiten `--help`; por ejemplo, `forge add --help`. Para elegir una base concreta, coloca `--db` antes del comando, como en `forge --db ./forge.db list`.

## Pruebas

Desde la raíz del repositorio, ejecuta la suite con `unittest`:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Las pruebas crean bases SQLite temporales y comprueban la inicialización repetible, conservación de los datos, consulta y listado de proyectos, además de los comandos principales de la CLI. No requieren instalar un framework de pruebas.

## Alcance actual

La lógica de aplicación valida y normaliza los nombres antes de persistirlos, separada de la CLI y del repositorio SQLite. La versión actual permite inicializar la base, añadir, listar, buscar, consultar, editar, archivar y restaurar proyectos. Todavía no incluye tareas, automatizaciones, filtros avanzados, salida JSON ni configuración interactiva.
