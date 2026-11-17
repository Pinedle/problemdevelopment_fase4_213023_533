# PROYECTO GITHUB: problemdevelopment_fase4_213023_533

## Descripción

**Software FJ** es una aplicación de escritorio desarrollada en Python para administrar clientes, servicios y reservas. Permite registrar clientes, crear y gestionar servicios, calcular costos y administrar el ciclo de vida de las reservas.

El proyecto corresponde a la actividad **Fase 4 - Diseño y Programación Orientada a Objetos** del curso Programación, grupo **213023_533**, de la Universidad Nacional Abierta y a Distancia (UNAD).

## Funcionalidades

- Registro y consulta de clientes, con validación de nombre, documento, correo electrónico y teléfono.
- Creación y administración de tres tipos de servicios:
  - Reserva de salas.
  - Alquiler de equipos.
  - Asesoría especializada.
- Activación y desactivación de servicios.
- Cálculo de costos con impuestos, descuentos y cargos aplicables.
- Creación, confirmación, procesamiento y cancelación de reservas.
- Registro de eventos y errores en un archivo de log.
- Interfaz gráfica con pestañas para clientes, servicios, cálculo de costos, reservas y registros.

## Tecnologías y dependencias

- **Python 3**
- **Tkinter** (`tkinter`, `tkinter.messagebox`, `tkinter.ttk`) para la interfaz gráfica.

El código también utiliza módulos de la biblioteca estándar de Python: `logging`, `os`, `re`, `abc`, `datetime`, `itertools` y `pathlib`.

**No se identificaron dependencias externas de terceros** en el archivo principal revisado. Por lo tanto, no se requiere instalar paquetes mediante `pip` para ejecutar esta versión. Tkinter normalmente viene incluido con Python para Windows.

## Estructura del repositorio

```text
problemdevelopment_fase4_213023_533/
│
├── logs/
│   └── (aquí se genera software_fj.log al ejecutar la aplicación)
│
├── .gitattributes
├── .gitignore
├── README.md
└── softwareFJ.py
```

## Requisitos

- Windows.
- Python 3 instalado, con soporte para Tkinter.
- Git, para clonar y actualizar el repositorio.

Para comprobar que Python está disponible, ejecuta en CMD o PowerShell:

```powershell
python --version
```

Para comprobar Tkinter:

```powershell
python -m tkinter
```

Este último comando debe abrir una pequeña ventana de prueba.

## Instalación y ejecución

1. Clona el repositorio:

   ```powershell
   git clone URL_DEL_REPOSITORIO
   ```

2. Ingresa a la carpeta del proyecto:

   ```powershell
   cd problemdevelopment_fase4_213023_533
   ```

3. Ejecuta la aplicación:

   ```powershell
   python softwareFJ.py
   ```

La aplicación crea la carpeta `logs` si no existe y registra los eventos en `logs/software_fj.log`.

## Trabajo colaborativo en GitHub

El equipo de desarrollo está conformado por:

| Integrante | Rama de trabajo |
|---|---|
| Lenyn Esteban Lozano Pineda | `lenynlozano_fase4` |
| Luís Ángel Padilla Soto | `LuisAngelPadilla_Fase4` |

### Recomendaciones de colaboración

1. Cada integrante debe realizar sus cambios en su propia rama.
2. Antes de comenzar a trabajar, actualizar la rama local con los cambios remotos correspondientes.
3. Realizar commits con mensajes claros que describan el cambio.
4. Publicar los cambios en la rama propia.
5. Revisar los cambios antes de integrarlos mediante Pull Request o el procedimiento acordado por el equipo.
6. Evitar trabajar directamente sobre la rama de otra persona sin coordinación.

### Ejemplos de comandos Git


Actualizar la información del repositorio remoto por línea de comandos:

1. git checkout      # Cambiar entre ramas (Branch) del proyecto.
2. git add .         # Adicionar cambios sobre cada uno de los archivos modificados.
3. git commit -m     # "Avances de cambios en el código y proyecto en general".
4. git push origin   # Subir cambios desde la rama local al repositorio en GitHub (Cloud).
5. git pull origin   # Entrega y descaarga los últimos cambios publicados en la rama.

# Se realizó el merge en el gitbush por línea de comandos

5. git merge         # Integrar los cambios entre cada una de las ramas

## Autores (Desarrolladores)

- Lenyn Esteban Lozano Pineda
- Luís Ángel Padilla Soto

**UNAD — Universidad Nacional Abierta y a Distancia**  
**Curso:** Programación  
**Grupo:** 213023_533  
**Actividad:** Fase 4 - Diseño y Programación Orientada a Objetos