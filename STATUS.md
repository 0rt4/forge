# Estado de Forge

## Objetivo

Desarrollar una herramienta local en Python para registrar y consultar proyectos de desarrollo utilizando SQLite.

Forge debe gestionar sus propios registros sin modificar el código fuente de los proyectos registrados.

## Estado actual

Primer incremento completado: modelo de proyecto y persistencia básica.

### Implementado

- Estructura inicial del paquete Python.
- Modelo `Project` con identificador, nombre, ruta y descripción.
- Repositorio SQLite.
- Inicialización de la tabla de proyectos.
- Guardado de proyectos.
- Consulta de proyectos por identificador.
- Tres pruebas automatizadas de persistencia.
- Pruebas ejecutadas correctamente con `unittest`.

### Pendiente

- Interfaz de línea de comandos (CLI).
- Registro de proyectos desde la terminal.
- Listado de proyectos registrados.
- Consulta de detalles de un proyecto desde la terminal.

## Siguiente incremento propuesto

Planificar una CLI mínima que permita registrar proyectos, listarlos y consultar sus detalles.

Antes de implementar, revisar el estado real del repositorio, identificar los cambios necesarios y presentar un plan para mi aprobación.

No ampliar el alcance sin autorización.

## Criterios para dar por terminado un incremento

- El código implementa únicamente el alcance aprobado.
- Las pruebas pertinentes pasan.
- Los cambios han sido revisados.
- La documentación refleja el estado real del proyecto.
- Se ha identificado el siguiente paso sin implementarlo automáticamente.
