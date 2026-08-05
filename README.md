
![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-orange.svg)

# 🔍 PathTracer

**PathTracer** es un potente buscador de archivos y carpetas con dos versiones: una para terminal y otra con interfaz gráfica (Tkinter). Permite realizar búsquedas rápidas y eficientes en el sistema de archivos con múltiples opciones de filtrado.

## 📸 Capturas de pantalla

### Versión Terminal
![[Captura de pantalla_20260805_125955.png]]


### Versión Tkinter (GUI)
![[Captura de pantalla_20260805_130054.png]]

## ✨ Características

### 🔍 **Búsqueda avanzada**
- Búsqueda por nombre
- Búsqueda por extensión (.txt, .mp4, .pdf, etc.)
- Búsqueda con comodines (`*` y `?`)
- Búsqueda específica (solo archivos o solo carpetas)
- Límite de resultados configurable

### 🎨 **Versión Terminal**
- Interfaz amigable con emojis y colores
- Estadísticas de tiempo de ejecución
- Menú interactivo
- Multiplataforma

### 🖱️ **Versión Tkinter (GUI)**
- **Interfaz moderna y personalizable** con temas oscuros
- **Resultados interactivos** con botones para cada archivo/carpeta:
  - ▶ Abrir: Abre el archivo/carpeta con su programa predeterminado
  - 📂 Carpeta: Abre la carpeta contenedora del archivo
  - 📋 Copiar: Copia la ruta al portapapeles
  - ℹ️ Info: Muestra información detallada
- **Tooltips** al pasar el mouse sobre los resultados
- **Scroll automático** para muchos resultados
- **Búsqueda en segundo plano** (no bloquea la interfaz)
- **Botón para detener** la búsqueda en cualquier momento
- **Atajos de teclado** (Ctrl+F para enfocar búsqueda)
- **Totalmente personalizable** (colores, fuentes, etc.)

## 📦 Requisitos

### Para ambas versiones:
- Python 3.6 o superior

### Para la versión GUI (Tkinter):
- Tkinter (incluido por defecto en Python)
- PIL/Pillow (opcional, para iconos)

```bash
# Instalar dependencias opcionales
pip install Pillow
```

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/amateo142857/PathTracer.git

# Entrar al directorio
cd PathTracer

# Dar permisos de ejecución (Linux/macOS)
chmod +x path_tracer_terminal.py path_tracer_tkinter.py
```

## 💻 Uso

### Versión Terminal
```bash
python path_tracer_terminal.py
```

### Versión Tkinter (GUI)
```bash
python path_tracer_tkinter.py
```

## 📖 Guía de uso

### Menú principal (Terminal)
```
============================================================
  🔍 BUSCADOR DE ARCHIVOS - VERSIÓN TERMINAL
============================================================
  1. Buscar por nombre
  2. Buscar por extensión
  3. Buscar con comodines
  4. Buscar carpetas
  5. Buscar archivos
  6. Salir
============================================================
```

### Interfaz Tkinter

#### Campo de búsqueda
- Escribe el nombre del archivo o carpeta
- Presiona Enter o haz clic en "Buscar"
- Usa Ctrl+F para enfocar el campo de búsqueda

#### Opciones de búsqueda
- **Tipo**: Archivos y carpetas, Solo archivos, Solo carpetas
- **Directorio**: Carpeta donde iniciar la búsqueda
- **Máx resultados**: Límite de resultados (dejar vacío = sin límite)

#### Resultados
Cada resultado muestra:
- **Nombre del archivo/carpeta** (no la ruta completa)
- **Tooltip** con la ruta completa al pasar el mouse
- **Botones de acción**:
  - 🚀 Abrir: Abre el elemento
  - 📂 Carpeta: Abre la carpeta contenedora
  - 📋 Copiar: Copia la ruta al portapapeles
  - ℹ️ Info: Muestra información detallada

### Ejemplos de uso

#### Buscar por nombre
```bash
📂 Directorio de búsqueda: /home/usuario/Documentos
🔍 Patrón de búsqueda: proyecto
📊 Máximo resultados: 10
```

#### Buscar por extensión
```bash
📂 Directorio: .
🔍 Extensión: .pdf
```

#### Buscar con comodines
```bash
📂 Directorio: .
🔍 Patrón: *foto*.jpg
📌 Tipo: archivos
```

## 🎨 Personalización

### Colores (Versión Tkinter)

Puedes personalizar los colores editando las variables al inicio de `buscador_tkinter.py`:

```python
# Tema Oscuro (por defecto)
COLOR_VENTANA = "#1e1e1e"
COLOR_FRAMES = "#2d2d2d"
COLOR_TEXTO = "#ffffff"
COLOR_BOTON_BG = "#4CAF50"

# Tema Claro
COLOR_VENTANA = "#f5f5f5"
COLOR_FRAMES = "#ffffff"
COLOR_TEXTO = "#333333"
COLOR_BOTON_BG = "#2196F3"
```

### Paletas predefinidas

| Tema | Fondo | Frames | Texto | Botones |
|------|-------|--------|-------|---------|
| Oscuro | #1e1e1e | #2d2d2d | #ffffff | #4CAF50 |
| Claro | #f5f5f5 | #ffffff | #333333 | #2196F3 |
| Azul | #0a192f | #172a45 | #e6f1ff | #64ffda |
| Rosa | #2d1b69 | #4a2d8c | #ffffff | #ff6bcd |
| Retro | #000000 | #0a0a0a | #00ff00 | #003300 |

## 📊 Ejemplo de salida

### Terminal
```
============================================================
🔍 BUSCANDO: 'proyecto'
📂 Directorio: /home/usuario/Documentos
📌 Tipo: ambos
============================================================

  📁 /home/usuario/Documentos/Proyectos
  📁 /home/usuario/Documentos/Proyectos/2024
  📄 /home/usuario/Documentos/proyecto_final.pdf
  📄 /home/usuario/Documentos/proyecto_ideas.txt

============================================================
✅ RESULTADOS:
  📁 Carpetas: 2
  📄 Archivos: 2
  📊 Total: 4
  ⏱️  Tiempo: 0.85 segundos
============================================================
```

### GUI
```
📄 proyecto_final.pdf    [🚀 Abrir] [📂 Carpeta] [📋 Copiar] [ℹ️ Info]
📄 proyecto_ideas.txt     [🚀 Abrir] [📂 Carpeta] [📋 Copiar] [ℹ️ Info]
📁 Proyectos              [🚀 Abrir] [📂 Carpeta] [📋 Copiar] [ℹ️ Info]
📁 Proyectos/2024         [🚀 Abrir] [📂 Carpeta] [📋 Copiar] [ℹ️ Info]
```

## 🛠️ Funciones principales

| Función | Descripción | Versión |
|---------|-------------|---------|
| `buscar_completo()` | Búsqueda completa con filtros | Ambas |
| `buscar_por_extension()` | Búsqueda por extensión | Ambas |
| `buscar_con_comodines()` | Búsqueda con comodines | Ambas |
| `buscar_carpetas_por_nombre()` | Búsqueda de carpetas | Ambas |
| `buscar_archivos_por_nombre()` | Búsqueda de archivos | Ambas |
| `abrir_archivo()` | Abrir archivo/carpeta | GUI |
| `abrir_carpeta_contenedora()` | Abrir carpeta contenedora | GUI |
| `copiar_ruta_al_portapapeles()` | Copiar ruta al portapapeles | GUI |
| `mostrar_info()` | Mostrar información detallada | GUI |

## 🐛 Solución de problemas

### Error: "Permission denied"
```bash
# En Linux/macOS, ejecuta con permisos adecuados
sudo python buscador.py
```

### Error: Tkinter no encontrado
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### Error: "xdg-open: not found" (Linux)
```bash
# Instalar xdg-utils
sudo apt install xdg-utils  # Ubuntu/Debian
sudo dnf install xdg-utils  # Fedora
```

### La búsqueda es muy lenta
- Limita los resultados con la opción de máximo resultados
- Busca en directorios más específicos
- Usa la versión GUI con búsqueda en segundo plano

### El programa no abre archivos en KDE/Dolphin
```bash
# Verificar que Dolphin esté instalado
which dolphin

# Instalar Dolphin si es necesario
sudo apt install dolphin  # Ubuntu/Debian
```

## 📁 Estructura del proyecto

```
PathTracer/
├── path_tracer_terminal.py  # Versión Terminal
├── path_tracer_tkinter.py   # Versión GUI
├── README.md                # Este archivo
├── LICENSE                  # Licencia MIT
└── img/                     # Iconos
    └── icono1.png
    └──terminal.png
    └── gui.png
```

## 🔄 Actualizaciones futuras

- [ ] Búsqueda por contenido de archivos
- [ ] Búsqueda por tamaño
- [ ] Búsqueda por fecha de modificación
- [ ] Modo oscuro/claro automático
- [ ] Guardar historial de búsquedas
- [ ] Exportar resultados a CSV/JSON
- [ ] Vista previa de archivos

## 🤝 Contribuir

1. Haz un Fork del proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Áreas de contribución
- Mejoras en la interfaz GUI
- Nuevas funcionalidades de búsqueda
- Optimización de rendimiento
- Soporte para más plataformas
- Documentación y ejemplos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Alejandro Mateo Ochoa**
- GitHub: [@amateo142857](https://github.com/amateo142857)

## 🙏 Agradecimientos

- Módulo `os` de Python por las funciones de sistema de archivos
- Módulo `fnmatch` por el soporte de comodines
- Tkinter por la interfaz gráfica
- Comunidad de Python por las herramientas estándar

## 📌 Notas adicionales

- El programa es **multiplataforma** (Windows, Linux, macOS)
- La versión Terminal usa solo módulos estándar de Python
- La versión GUI usa Tkinter (incluido con Python)
- Ideal para búsquedas rápidas en cualquier entorno

---

⭐ **Si te gusta este proyecto, no olvides darle una estrella en GitHub!**

## 📞 Contacto

¿Tienes preguntas o sugerencias? Abre un [Issue](https://github.com/amateo142857/PathTracer/issues) o contáctame en GitHub.

