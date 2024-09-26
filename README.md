# Control de Biodigestores

Este proyecto es una aplicación web desarrollada con Flask para llevar el control de los biodigestores instalados en centros educativos. El sistema permite gestionar la información de los centros, biodigestores y contactos asociados. Además, está integrado con una base de datos SQL Server para almacenar y consultar la información de manera eficiente.

## Funcionalidades principales

- **Gestión de centros educativos**: Registro y consulta de centros educativos con detalles de ubicación (municipio y departamento).
- **Control de biodigestores**: Asignación de biodigestores a centros educativos, especificando el modelo y su uso (baños o desechos orgánicos).
- **Gestión de contactos**: Agregar, editar y eliminar contactos asociados a cada centro educativo. Posibilidad de incluir múltiples números de teléfono con diferentes tipos (celular, domicilio, trabajo).
- **Autenticación**: Sistema de login utilizando Flask-Login para gestionar usuarios.
- **CRUD de contactos**: Funcionalidades completas para crear, modificar y eliminar contactos.

## Tecnologías utilizadas

- **Flask**: Framework de desarrollo web en Python.
- **SQL Server**: Base de datos relacional para el almacenamiento de la información.
- **HTML/CSS**: Diseño de la interfaz de usuario utilizando plantillas con Jinja2.
- **JavaScript**: Interactividad en la interfaz de usuario (gestión de modales y formularios dinámicos).
- **Flask-Login**: Autenticación de usuarios.

