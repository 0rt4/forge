# Estado de Forge

## Objetivo

Desarrollar una herramienta local en Python para registrar y consultar proyectos de desarrollo utilizando SQLite.

Forge debe gestionar sus propios registros sin modificar el código fuente de los proyectos registrados.

## Estado actual

Forge cuenta con persistencia SQLite y una CLI para gestionar proyectos.

### Implementado

- Estructura inicial del paquete Python.
- Modelo `Project` con identificador, nombre, ruta y descripción.
- Repositorio SQLite.
- Inicialización de la tabla de proyectos.
- Guardado de proyectos.
- Consulta de proyectos por identificador.
- Pruebas automatizadas de persistencia, reglas de aplicación y CLI.
- CLI para inicializar, añadir, listar, consultar, editar, archivar y restaurar proyectos.
- Búsqueda parcial sin distinción de mayúsculas en nombre y ruta; por defecto omite archivados.

### Pendiente

- Experiencia de instalación y distribución pulida para usuarios finales.
- Definir si el MVP requiere filtros adicionales o exportación de datos.

## Siguiente incremento propuesto

Evaluar la experiencia de instalación y distribución desde una copia limpia del proyecto.

## Criterios para dar por terminado un incremento

- El código implementa únicamente el alcance aprobado.
- Las pruebas pertinentes pasan.
- Los cambios han sido revisados.
- La documentación refleja el estado real del proyecto.
- Se ha identificado el siguiente paso sin implementarlo automáticamente.
