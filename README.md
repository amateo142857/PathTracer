```markdown
![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
```

```markdown
# 🔍 PathTracer - Terminal

Un potente buscador de archivos y carpetas para la terminal, escrito en Python. Permite realizar búsquedas rápidas y eficientes en el sistema de archivos con múltiples opciones de filtrado.

## ✨ Características

- 🔍 **Búsqueda por nombre** - Encuentra archivos y carpetas por coincidencia de texto
- 📄 **Búsqueda por extensión** - Filtra archivos por su extensión (.txt, .mp4, .pdf, etc.)
- 🎯 **Búsqueda con comodines** - Usa `*` y `?` para búsquedas avanzadas
- 📁 **Búsqueda específica** - Busca solo carpetas o solo archivos
- 📊 **Límite de resultados** - Controla el número máximo de resultados
- ⏱️ **Estadísticas de tiempo** - Muestra el tiempo de ejecución de cada búsqueda
- 🎨 **Interfaz amigable** - Emojis y colores para mejor legibilidad
- 🔄 **Multiplataforma** - Funciona en Windows, Linux y macOS

## 📦 Requisitos

- Python 3.6 o superior
- No requiere dependencias externas (solo módulos estándar)

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/buscador-archivos-terminal.git

# Entrar al directorio
cd buscador-archivos-terminal

# Dar permisos de ejecución (Linux/macOS)
chmod +x buscador.py
```

## 💻 Uso

### Ejecutar el programa

```bash
python buscador.py
```

### Menú principal

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

### Ejemplos de uso

#### 1. Buscar por nombre
```
📂 Directorio de búsqueda (Enter para actual): /home/usuario/Documentos
🔍 Patrón de búsqueda: proyecto
📊 Máximo resultados (Enter para sin límite): 10
```

#### 2. Buscar por extensión
```
📂 Directorio de búsqueda (Enter para actual): .
🔍 Extensión (ej: .txt, .mp4): .pdf
```

#### 3. Buscar con comodines
```
📂 Directorio de búsqueda (Enter para actual): .
🔍 Patrón (ej: *.txt, *proyecto*): *foto*.jpg
📌 Tipo (archivos/carpetas/ambos): archivos
```

#### 4. Buscar carpetas
```
📂 Directorio de búsqueda (Enter para actual): .
🔍 Nombre de carpeta: python
```

#### 5. Buscar archivos
```
📂 Directorio de búsqueda (Enter para actual): .
🔍 Nombre de archivo: informe
📊 Máximo resultados (Enter para sin límite): 20
```

## 📊 Ejemplo de salida

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

## 🛠️ Funciones principales

| Función | Descripción |
|---------|-------------|
| `buscar_completo()` | Búsqueda completa con opciones de filtrado |
| `buscar_por_extension()` | Busca archivos por extensión específica |
| `buscar_con_comodines()` | Búsqueda con comodines (*, ?) |
| `buscar_carpetas_por_nombre()` | Busca carpetas por coincidencia en el nombre |
| `buscar_archivos_por_nombre()` | Busca archivos por coincidencia en el nombre |
| `limpiar_pantalla()` | Limpia la terminal (multiplataforma) |

## 🔧 Personalización

### Cambiar directorio por defecto

Modifica la variable en la función `buscar_por_nombre()`:
```python
directorio = input("📂 Directorio de búsqueda (Enter para actual): ").strip()
if not directorio:
    directorio = '/ruta/personalizada'  # Cambia aquí
```

## 🐛 Solución de problemas

### Error: "Permission denied"
```bash
# En Linux/macOS, ejecuta con permisos adecuados
sudo python buscador.py
```

### Error: "El directorio no existe"
- Verifica que la ruta ingresada sea correcta
- Usa rutas absolutas o relativas válidas

### La búsqueda es muy lenta
- Limita los resultados con la opción de máximo resultados
- Busca en directorios más específicos

## 📝 Contribuir

1. Haz un Fork del proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Alejandro Mateo Ochoa**
- GitHub: [@amateo142857](https://github.com/amateo142857)

## 🙏 Agradecimientos

- Módulo `os` de Python por las funciones de sistema de archivos
- Módulo `fnmatch` por el soporte de comodines
- Comunidad de Python por las herramientas estándar

## 📌 Notas adicionales

- El programa es **multiplataforma** (Windows, Linux, macOS)
- No requiere instalación de dependencias externas
- Usa solo módulos de la biblioteca estándar de Python
- Ideal para búsquedas rápidas en entornos sin interfaz gráfica

---

⭐ **Si te gusta este proyecto, no olvides darle una estrella en GitHub!**
```




