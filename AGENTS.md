# Instrucciones para trabajar en Forge

## Objetivo del proyecto

Forge es una herramienta local desarrollada en Python para registrar y consultar proyectos de desarrollo.

Actualmente, Forge mantiene los datos de sus proyectos en SQLite. Su objetivo inicial es catalogar directorios existentes sin modificar el código fuente de esos proyectos.

## Forma de trabajo

- Comunícate conmigo en español y explica las decisiones técnicas relevantes de forma clara.
- Antes de implementar una funcionalidad nueva o un cambio significativo, inspecciona el código relacionado y presenta un plan.
- No implementes el plan hasta que yo lo autorice explícitamente.
- Limita los cambios al alcance aprobado. No añadas funcionalidades adicionales por iniciativa propia.
- Prioriza soluciones sencillas, legibles y fáciles de probar.
- No crees abstracciones o capas arquitectónicas sin una necesidad concreta.
- No añadas dependencias externas sin explicar primero por qué son necesarias.
- No sobrescribas ni descartes cambios existentes sin mi autorización.
- No modifiques los archivos de los proyectos que Forge registra. Forge gestiona sus propios registros, no el contenido de esos proyectos.
- No elimines directorios de proyectos al modificar o archivar sus registros.
<<<<<<< Updated upstream
- No dejes comentarios en el codigo a menos que sea necesario detallar un algoritmo complejo
=======
>>>>>>> Stashed changes

## Código y pruebas

- Respeta la estructura y las convenciones existentes del proyecto.
- Añade o modifica pruebas cuando cambie el comportamiento.
- Ejecuta las pruebas pertinentes después de implementar cambios.
- Comando actual de pruebas:

  `PYTHONPATH=src python -W error::ResourceWarning -m unittest discover -s tests -v`

- Antes de dar por terminado un cambio, revisa las diferencias y resume los archivos modificados, las decisiones relevantes y los resultados de las pruebas.

## Documentación

- Mantén README.md enfocado en el propósito, la instalación y el uso de Forge.
- Mantén STATUS.md actualizado según el código y las pruebas reales.
- Distingue siempre entre funcionalidades implementadas y funcionalidades pendientes.
- Si encuentras que la documentación contradice el código, señala la discrepancia en lugar de asumir que la documentación es correcta.
