import os
import time
import json
import subprocess
import fnmatch
import platform
import tkinter as tk
from datetime import datetime, date
from threading import Thread
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

import customtkinter as ctk

# ============ PALETA DE COLORES (agradable, estilo "Nord/Catppuccin") ============

COLOR_FONDO          = "#1e1e2e"   # fondo principal (azul noche suave)
COLOR_FONDO_2        = "#252537"   # fondo secundario
COLOR_FONDO_3        = "#313244"   # tarjetas / inputs
COLOR_BORDE          = "#45475a"   # bordes sutiles
COLOR_TEXTO          = "#cdd6f4"   # texto principal
COLOR_TEXTO_SUAVE    = "#a6adc8"   # texto secundario
COLOR_ACENTO         = "#89b4fa"   # azul pastel (acento principal)
COLOR_ACENTO_HOVER   = "#74a8f7"
COLOR_VERDE          = "#a6e3a1"   # verde pastel
COLOR_AMARILLO       = "#f9e2af"   # amarillo pastel
COLOR_ROJO           = "#f38ba8"   # rojo pastel
COLOR_MORADO         = "#cba6f7"   # morado pastel

# ============ CONFIGURACIÓN GLOBAL DE CTK ============

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ============ RUTAS DE PERSISTENCIA ============

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_FAVORITOS = os.path.join(BASE_DIR, "favoritos.json")
ARCHIVO_HISTORIAL = os.path.join(BASE_DIR, "historial.json")

MAX_HISTORIAL = 500  # límite de entradas guardadas en historial.json

# ============ CONSTANTES ============

CARPETAS_EXCLUIDAS = {
    # Sistema Windows
    "Windows", "System32", "SysWOW64", "WinSxS",
    "$Recycle.Bin", "$RECYCLE.BIN",
    "System Volume Information",
    "Recovery", "PerfLogs",
    "ProgramData",
    # Cachés y configuraciones de usuario
    "AppData", "Application Data", "Local Settings",
    "Temporary Internet Files", "Cache", "Caches",
    # Desarrollo
    "node_modules", ".git", ".svn", ".hg",
    "__pycache__", ".venv", "venv", ".env",
    "dist", "build", ".next", ".nuxt",
    # Editores
    ".vscode", ".idea", ".vs",
    # macOS / Linux
    ".Trash", ".Trashes", "lost+found",
    "proc", "sys", "dev", "run",
    # Linux extra (para que buscar en / no sea eterno)
    "snap", "flatpak", "docker", "containers",
    "var/cache", "var/lib/docker", "var/lib/snapd",
}

# ============ ICONOS POR TIPO DE ARCHIVO ============

TIPOS_ARCHIVO = {
    'video': {
        'ext': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                '.mpeg', '.mpg', '.m4v', '.3gp', '.ts', '.vob', '.rmvb'],
        'icono': '🎬',
        'color': '#fab387'
    },
    'audio': {
        'ext': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
                '.opus', '.aiff', '.mid', '.midi'],
        'icono': '🎵',
        'color': '#cba6f7'
    },
    'imagen': {
        'ext': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
                '.webp', '.svg', '.ico', '.raw', '.heic'],
        'icono': '🖼️',
        'color': '#89dceb'
    },
    'documento': {
        'ext': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.md',
                '.tex', '.pages'],
        'icono': '📄',
        'color': '#a6e3a1'
    },
    'hoja_calculo': {
        'ext': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
        'icono': '📊',
        'color': '#94e2d5'
    },
    'presentacion': {
        'ext': ['.ppt', '.pptx', '.odp', '.key'],
        'icono': '📽️',
        'color': '#f38ba8'
    },
    'comprimido': {
        'ext': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
                '.iso', '.cab'],
        'icono': '🗜️',
        'color': '#f9e2af'
    },
    'codigo': {
        'ext': ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
                '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
                '.html', '.css', '.scss', '.sql', '.sh', '.bat', '.ps1',
                '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg','.git'],
        'icono': '💻',
        'color': '#89b4fa'
    },
    'ejecutable': {
        'ext': ['.exe', '.msi', '.app', '.apk', '.deb', '.rpm', '.dmg',
                '.bin', '.run'],
        'icono': '⚙️',
        'color': '#b4befe'
    },
    'fuente': {
        'ext': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
        'icono': '🔤',
        'color': '#f5c2e7'
    },
    'base_datos': {
        'ext': ['.db', '.sqlite', '.sqlite3', '.mdb', '.accdb'],
        'icono': '🗄️',
        'color': '#9399b2'
    },
    'diseno': {
        'ext': ['.psd', '.ai', '.xd', '.fig', '.sketch', '.blend',
                '.obj', '.fbx', '.stl', '.3ds'],
        'icono': '🎨',
        'color': '#f9e2af'
    },
}


def obtener_icono_y_color(ruta, es_archivo):
    """Devuelve (icono, color) según el tipo de archivo o carpeta."""
    if not es_archivo:
        return '📁', COLOR_AMARILLO
    ext = os.path.splitext(ruta)[1].lower()
    for _, datos in TIPOS_ARCHIVO.items():
        if ext in datos['ext']:
            return datos['icono'], datos['color']
    return '📄', COLOR_TEXTO


# ============ UTILIDADES DE SISTEMA ============

def obtener_unidades():
    """Devuelve una lista con las raíces de todas las unidades disponibles."""
    unidades = []

    if platform.system() == "Windows":
        for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            raiz = f"{letra}:\\"
            if os.path.exists(raiz):
                unidades.append(raiz)
    else:
        unidades.append("/")
        for base in ("/Volumes", "/media", "/mnt"):
            if os.path.isdir(base):
                try:
                    for sub in os.listdir(base):
                        ruta = os.path.join(base, sub)
                        if os.path.isdir(ruta):
                            unidades.append(ruta)
                except PermissionError:
                    pass

    return unidades


def walk_seguro(directorio):
    """
    os.walk robusto: ignora errores de permisos y filtra carpetas
    excluidas (Windows, caches, etc.).
    """
    def _on_error(_err):
        pass

    for root, dirs, files in os.walk(directorio, onerror=_on_error):
        dirs[:] = [
            d for d in dirs
            if d not in CARPETAS_EXCLUIDAS and not d.startswith('$')
        ]
        yield root, dirs, files


# ============ FUNCIONES DEL BUSCADOR ============

def buscar_completo(directorio, patron, tipo="ambos", max_resultados=None):
    resultados = {'archivos': [], 'carpetas': [], 'total': 0}
    contador = 0
    inicio = time.time()

    for root, dirs, files in walk_seguro(directorio):
        if max_resultados and contador >= max_resultados:
            break

        if tipo in ["carpetas", "ambos"]:
            for carpeta in dirs:
                if max_resultados and contador >= max_resultados:
                    break
                if patron.lower() in carpeta.lower():
                    ruta = os.path.join(root, carpeta)
                    resultados['carpetas'].append(ruta)
                    resultados['total'] += 1
                    contador += 1

        if tipo in ["archivos", "ambos"]:
            for archivo in files:
                if max_resultados and contador >= max_resultados:
                    break
                if patron.lower() in archivo.lower():
                    ruta = os.path.join(root, archivo)
                    resultados['archivos'].append(ruta)
                    resultados['total'] += 1
                    contador += 1

    fin = time.time()
    return resultados, fin - inicio


def buscar_con_comodines(directorio, patron, tipo="ambos", max_resultados=None):
    resultados = []
    for root, dirs, files in walk_seguro(directorio):
        if tipo in ["archivos", "ambos"]:
            for archivo in files:
                if fnmatch.fnmatch(archivo.lower(), patron.lower()):
                    resultados.append(os.path.join(root, archivo))
                    if max_resultados and len(resultados) >= max_resultados:
                        return resultados
        if tipo in ["carpetas", "ambos"]:
            for carpeta in dirs:
                if fnmatch.fnmatch(carpeta.lower(), patron.lower()):
                    resultados.append(os.path.join(root, carpeta))
                    if max_resultados and len(resultados) >= max_resultados:
                        return resultados
    return resultados


def buscar_carpetas_por_nombre(directorio, patron, max_resultados=None):
    resultados = []
    for root, dirs, _ in walk_seguro(directorio):
        for carpeta in dirs:
            if patron.lower() in carpeta.lower():
                resultados.append(os.path.join(root, carpeta))
                if max_resultados and len(resultados) >= max_resultados:
                    return resultados
    return resultados


def buscar_archivos_por_nombre(directorio, patron, max_resultados=None):
    resultados = []
    for root, _, files in walk_seguro(directorio):
        for archivo in files:
            if patron.lower() in archivo.lower():
                resultados.append(os.path.join(root, archivo))
                if max_resultados and len(resultados) >= max_resultados:
                    return resultados
    return resultados


# ============ FUNCIONES PARA ABRIR ARCHIVOS ============

def abrir_archivo(ruta):
    if not os.path.exists(ruta):
        messagebox.showerror("Error", f"La ruta no existe:\n{ruta}")
        return
    try:
        if platform.system() == 'Windows':
            os.startfile(ruta)  # type: ignore
        elif platform.system() == 'Darwin':
            subprocess.run(['open', ruta])
        else:
            subprocess.run(['xdg-open', ruta],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir:\n{str(e)}")


def abrir_carpeta_contenedora(ruta):
    if not os.path.exists(ruta):
        messagebox.showerror("Error", f"La ruta no existe:\n{ruta}")
        return
    try:
        carpeta = os.path.dirname(ruta) if os.path.isfile(ruta) else ruta
        abrir_archivo(carpeta)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")


def copiar_ruta_al_portapapeles(ruta):
    try:
        ventana.clipboard_clear()
        ventana.clipboard_append(ruta)
        mostrar_toast("📋 Ruta copiada", COLOR_VERDE)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar:\n{str(e)}")


# ============ PERSISTENCIA: FAVORITOS E HISTORIAL ============

def _cargar_json(archivo, defecto):
    try:
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return defecto


def _guardar_json(archivo, datos):
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{archivo}\n\n{e}")
        return False


def cargar_favoritos():
    return _cargar_json(ARCHIVO_FAVORITOS, [])


def guardar_favoritos(favs):
    return _guardar_json(ARCHIVO_FAVORITOS, favs)


def cargar_historial():
    return _cargar_json(ARCHIVO_HISTORIAL, [])


def guardar_historial(hist):
    return _guardar_json(ARCHIVO_HISTORIAL, hist)


def agregar_al_historial(termino, tipo, directorio, num_resultados):
    """Añade una entrada al historial. Cada entrada lleva fecha y hora."""
    hist = cargar_historial()
    hist.append({
        "termino": termino,
        "tipo": tipo,
        "directorio": directorio,
        "resultados": num_resultados,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S"),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    # Recortar si excede el máximo
    if len(hist) > MAX_HISTORIAL:
        hist = hist[-MAX_HISTORIAL:]
    guardar_historial(hist)


def historial_de_hoy():
    hoy = date.today().strftime("%Y-%m-%d")
    return [h for h in cargar_historial() if h.get("fecha") == hoy]


# ============ VARIABLES GLOBALES ============

ventana = None
entry_busqueda = None
entry_dir = None
entry_max = None
tipo_busqueda = None
dir_busqueda = None
max_resultados_var = None
label_estado = None
label_info = None
btn_buscar = None
btn_detener = None
frame_resultados = None
canvas_resultados = None
busqueda_activa = False
toast_actual = None

# Estado real: ¿el usuario quiere buscar en todos los discos?
modo_todos_discos = False

# Panel avanzado / filtro de extensiones
btn_avanzado = None
panel_avanzado = None
label_filtro_estado = None
panel_avanzado_visible = False
extensiones_seleccionadas = set()   # ej: {".txt", ".py"}
filtro_extensiones_activo = False
_vars_extensiones = {}              # ext -> tk.BooleanVar

# Referencia al popup de acciones abierto (para cerrarlo si se abre otro)
_popup_acciones_actual = None


# ============ UTILIDADES DE UI ============

def formatear_tamaño(bytes_):
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_ < 1024.0:
            return f"{bytes_:.1f} {unidad}"
        bytes_ /= 1024.0
    return f"{bytes_:.1f} TB"


def mostrar_toast(mensaje, color=COLOR_ACENTO):
    """Muestra un pequeño aviso flotante en la esquina inferior derecha."""
    global toast_actual
    if toast_actual is not None:
        try:
            toast_actual.destroy()
        except Exception:
            pass

    toast = ctk.CTkToplevel(ventana)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.configure(fg_color=COLOR_FONDO_3)

    frame = ctk.CTkFrame(toast, fg_color=COLOR_FONDO_3,
                         border_color=color, border_width=2,
                         corner_radius=12)
    frame.pack(fill="both", expand=True, padx=1, pady=1)

    ctk.CTkLabel(frame, text=mensaje, text_color=color,
                 font=("Segoe UI", 12, "bold")).pack(padx=18, pady=10)

    ventana.update_idletasks()
    ancho = 320
    alto = 50
    x = ventana.winfo_rootx() + ventana.winfo_width() - ancho - 25
    y = ventana.winfo_rooty() + ventana.winfo_height() - alto - 25
    toast.geometry(f"{ancho}x{alto}+{x}+{y}")

    toast_actual = toast
    ventana.after(2200, lambda: _cerrar_toast(toast))


def _cerrar_toast(toast):
    try:
        toast.destroy()
    except Exception:
        pass


# ============ POPUP DE ACCIONES (BOTÓN ⋮) ============

def _cerrar_popup_acciones(_event=None):
    """Cierra el popup de acciones si está abierto."""
    global _popup_acciones_actual
    if _popup_acciones_actual is not None:
        try:
            _popup_acciones_actual.destroy()
        except Exception:
            pass
        _popup_acciones_actual = None


def abrir_popup_acciones(ruta, es_archivo, lbl_fav, widget_ancla):
    """
    Abre una ventana flotante pequeña con las acciones para una ruta.
    Se cierra al pulsar una acción, al hacer clic fuera o con Escape.

    Lógica de botones:
      - Archivo   → Abrir archivo / Abrir carpeta contenedora / Copiar / Fav / Info
      - Carpeta   → Abrir carpeta   / Copiar / Fav / Info
    """
    global _popup_acciones_actual

    # Si ya hay un popup abierto, lo cerramos primero
    _cerrar_popup_acciones()

    nombre = os.path.basename(ruta)
    icono, color = obtener_icono_y_color(ruta, es_archivo)
    ya_fav = es_favorito(ruta)

    popup = ctk.CTkToplevel(ventana)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(fg_color=COLOR_FONDO_2)
    _popup_acciones_actual = popup

    # Marco con borde de color según tipo
    marco = ctk.CTkFrame(popup,
                         fg_color=COLOR_FONDO_2,
                         border_color=color,
                         border_width=2,
                         corner_radius=14)
    marco.pack(fill="both", expand=True, padx=1, pady=1)

    # ---- Cabecera con icono + nombre ----
    cab = ctk.CTkFrame(marco, fg_color="transparent")
    cab.pack(fill="x", padx=14, pady=(12, 6))

    ctk.CTkLabel(cab,
                 text=f"{icono}",
                 font=("Segoe UI", 18, "bold"),
                 text_color=color,
                 width=28).pack(side="left")

    ctk.CTkLabel(cab,
                 text=nombre,
                 font=("Segoe UI", 13, "bold"),
                 text_color=color,
                 anchor="w",
                 wraplength=300,
                 justify="left").pack(side="left", fill="x", expand=True, padx=(6, 0))

    # ---- Ruta completa (pequeña, gris) ----
    ctk.CTkLabel(marco,
                 text=ruta,
                 font=("Segoe UI", 9),
                 text_color=COLOR_TEXTO_SUAVE,
                 anchor="w",
                 wraplength=340,
                 justify="left").pack(fill="x", padx=14, pady=(0, 10))

    # ---- Separador ----
    sep = ctk.CTkFrame(marco, height=1, fg_color=COLOR_BORDE)
    sep.pack(fill="x", padx=10, pady=(0, 8))

    # ---- Botones de acción ----
    def _accion_y_cerrar(fn):
        def _wrapper():
            _cerrar_popup_acciones()
            fn()
        return _wrapper

    fila_botones = ctk.CTkFrame(marco, fg_color="transparent")
    fila_botones.pack(fill="x", padx=10, pady=(0, 12))

    def _crear_boton(texto, comando, fg, hover, text_color="#1e1e2e"):
        return ctk.CTkButton(
            fila_botones,
            text=texto,
            command=comando,
            width=300, height=32,
            corner_radius=8,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            font=("Segoe UI", 11, "bold"),
            anchor="w")

    # Abrir (solo si es archivo → "Abrir archivo" / "Abrir carpeta contenedora")
    if es_archivo:
        _crear_boton("🚀  Abrir archivo",
                     _accion_y_cerrar(lambda: abrir_archivo(ruta)),
                     COLOR_ACENTO, COLOR_ACENTO_HOVER).pack(pady=2)

        _crear_boton("📁  Abrir carpeta contenedora",
                     _accion_y_cerrar(lambda: abrir_carpeta_contenedora(ruta)),
                     COLOR_FONDO_3, "#4a4c63", COLOR_TEXTO).pack(pady=2)

    else:
        # Es una carpeta: solo "Abrir carpeta"
        _crear_boton("📂  Abrir carpeta",
                     _accion_y_cerrar(lambda: abrir_archivo(ruta)),
                     COLOR_ACENTO, COLOR_ACENTO_HOVER).pack(pady=2)

    # Copiar ruta (siempre)
    _crear_boton("📋  Copiar ruta",
                 _accion_y_cerrar(lambda: copiar_ruta_al_portapapeles(ruta)),
                 COLOR_FONDO_3, "#4a4c63", COLOR_TEXTO).pack(pady=2)

    # Favorito (toggle, siempre)
    texto_fav = "💔  Quitar de favoritos" if ya_fav else "⭐  Añadir a favoritos"

    def _toggle_fav():
        toggle_favorito_ruta(ruta, lbl_fav)
        try:
            lbl_fav.configure(
                text="⭐" if es_favorito(ruta) else "☆",
                text_color=(COLOR_AMARILLO if es_favorito(ruta)
                            else COLOR_BORDE))
        except Exception:
            pass

    _crear_boton(texto_fav,
                 _accion_y_cerrar(_toggle_fav),
                 COLOR_AMARILLO, "#f5d78a").pack(pady=2)

    # Información (siempre)
    _crear_boton("ℹ️  Información",
                 _accion_y_cerrar(lambda: mostrar_info(ruta)),
                 COLOR_MORADO, "#b18ef0").pack(pady=2)

    # ---- Posicionamiento junto al widget ancla ----
    popup.update_idletasks()
    ancho = 380
    alto = popup.winfo_reqheight()
    if alto < 200:
        alto = 320

    x = widget_ancla.winfo_rootx() + widget_ancla.winfo_width() - ancho
    y = widget_ancla.winfo_rooty() + widget_ancla.winfo_height() + 4

    # Si se sale de la pantalla por abajo, abre arriba del ancla
    if y + alto > ventana.winfo_screenheight() - 10:
        y = widget_ancla.winfo_rooty() - alto - 4
    if x < 10:
        x = 10

    popup.geometry(f"{ancho}x{alto}+{x}+{y}")

    # ---- Cierre al hacer clic fuera o Escape ----
    def _on_click_outside(event):
        try:
            if event.widget.winfo_toplevel() != popup:
                _cerrar_popup_acciones()
        except Exception:
            _cerrar_popup_acciones()

    ventana.bind("<Button-1>", _on_click_outside, add="+")
    popup.bind("<Escape>", lambda e: _cerrar_popup_acciones())

    popup.focus_force()

    def _on_destroy(_e=None):
        global _popup_acciones_actual
        if _popup_acciones_actual == popup:
            _popup_acciones_actual = None

    popup.bind("<Destroy>", _on_destroy)


# ============ FUNCIONES DE TKINTER ============

def centrar_ventana():
    ventana.update_idletasks()
    w = ventana.winfo_width()
    h = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (w // 2)
    y = (ventana.winfo_screenheight() // 2) - (h // 2)
    ventana.geometry(f'{w}x{h}+{x}+{y}')


def on_frame_configure(event=None):
    canvas_resultados.configure(scrollregion=canvas_resultados.bbox('all'))


def on_canvas_configure(event):
    canvas_resultados.itemconfig(1, width=event.width - 5)


def seleccionar_directorio():
    global modo_todos_discos
    directorio = filedialog.askdirectory(title="Seleccionar directorio de búsqueda")
    if directorio:
        modo_todos_discos = False
        dir_busqueda.set(directorio)
        entry_dir.delete(0, "end")
        entry_dir.insert(0, directorio)


def seleccionar_todos_los_discos():
    global modo_todos_discos
    modo_todos_discos = True
    unidades = obtener_unidades()
    resumen = ", ".join(u.rstrip("\\/") or u for u in unidades)
    entry_dir.delete(0, "end")
    entry_dir.insert(0, f"💽 Todos los discos ({resumen})")
    mostrar_toast(f"💽 Se buscará en: {resumen}", COLOR_MORADO)


def _on_dir_escrito(event=None):
    global modo_todos_discos
    teclas_ignoradas = {"Left", "Right", "Up", "Down", "Home", "End",
                        "Shift_L", "Shift_R", "Control_L", "Control_R"}
    if modo_todos_discos and event is not None and event.keysym not in teclas_ignoradas:
        modo_todos_discos = False
    dir_busqueda.set(entry_dir.get())


def limpiar_resultados():
    global frame_resultados
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    label_info.configure(text="")


def mostrar_resultado(ruta, es_archivo):
    """
    Muestra una tarjeta de resultado SIN botones visibles.
    La interacción se hace con el botón ⋮ que abre un popup flotante.
    """
    nombre = os.path.basename(ruta)
    icono, color = obtener_icono_y_color(ruta, es_archivo)

    card = ctk.CTkFrame(frame_resultados,
                        fg_color=COLOR_FONDO_2,
                        corner_radius=10,
                        border_width=1,
                        border_color=COLOR_BORDE)
    card.pack(fill="x", pady=4, padx=4)

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=12, pady=10)

    ya_fav = es_favorito(ruta)
    texto = f"{icono}  {nombre}"
    label_nombre = ctk.CTkLabel(inner,
                                text=texto,
                                text_color=color,
                                font=("Segoe UI", 13, "bold"),
                                anchor="w")
    label_nombre.pack(side="left", fill="x", expand=True)

    lbl_fav = ctk.CTkLabel(inner,
                           text="⭐" if ya_fav else "☆",
                           font=("Segoe UI", 14, "bold"),
                           text_color=COLOR_AMARILLO if ya_fav else COLOR_BORDE)
    lbl_fav.pack(side="right", padx=(6, 0))

    btn_menu = ctk.CTkButton(inner, text="⋮",
                             width=32, height=28,
                             corner_radius=8,
                             fg_color=COLOR_FONDO_3,
                             hover_color=COLOR_ACENTO,
                             text_color=COLOR_TEXTO,
                             font=("Segoe UI", 13, "bold"))
    btn_menu.pack(side="right")

    btn_menu.configure(
        command=lambda: abrir_popup_acciones(ruta, es_archivo, lbl_fav, btn_menu))

    # ---- tooltip con la ruta completa (solo hover) ----
    def mostrar_tooltip(event):
        tooltip = tk.Toplevel(card)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
        tooltip.configure(bg=COLOR_BORDE)
        tk.Label(tooltip, text=ruta,
                 bg=COLOR_FONDO_3, fg=COLOR_TEXTO,
                 font=("Segoe UI", 9),
                 padx=8, pady=4).pack(padx=1, pady=1)
        card.tooltip = tooltip

    def ocultar_tooltip(event):
        if hasattr(card, 'tooltip'):
            try:
                card.tooltip.destroy()
            except Exception:
                pass

    for w in (card, inner, label_nombre, lbl_fav):
        w.bind("<Enter>", mostrar_tooltip)
        w.bind("<Leave>", ocultar_tooltip)


def mostrar_info(ruta):
    if not os.path.exists(ruta):
        messagebox.showerror("Error", "La ruta ya no existe")
        return
    nombre = os.path.basename(ruta)
    info = f"📂 Nombre: {nombre}\n"
    info += f"📌 Ruta: {ruta}\n\n"
    if os.path.isfile(ruta):
        info += f"📄 Tipo: Archivo\n"
        info += f"📏 Tamaño: {formatear_tamaño(os.path.getsize(ruta))}\n"
        info += f"📅 Modificado: {time.ctime(os.path.getmtime(ruta))}\n"
        info += f"🏷️ Extensión: {os.path.splitext(ruta)[1] or 'Sin extensión'}\n"
    else:
        info += f"📁 Tipo: Carpeta\n"
        info += f"📅 Modificado: {time.ctime(os.path.getmtime(ruta))}\n"
        try:
            info += f"📊 Contenido: {len(os.listdir(ruta))} elementos\n"
        except Exception:
            info += "📊 Contenido: No accesible\n"
    messagebox.showinfo(f"Información: {nombre}", info)


# ============ FAVORITOS ============

def es_favorito(ruta):
    """Devuelve True si la ruta ya está guardada como favorita (tipo ruta)."""
    for fav in cargar_favoritos():
        if fav.get("tipo") == "ruta" and fav.get("valor") == ruta:
            return True
    return False


def toggle_favorito_ruta(ruta, etiqueta_estrella=None):
    """Añade o quita una ruta de los favoritos."""
    favs = cargar_favoritos()
    existente = None
    for f in favs:
        if f.get("tipo") == "ruta" and f.get("valor") == ruta:
            existente = f
            break

    if existente:
        favs.remove(existente)
        guardar_favoritos(favs)
        if etiqueta_estrella is not None:
            try:
                etiqueta_estrella.configure(text="☆", text_color=COLOR_BORDE)
            except Exception:
                pass
        mostrar_toast("💔 Quitado de favoritos", COLOR_ROJO)
    else:
        favs.append({
            "tipo": "ruta",
            "valor": ruta,
            "nombre": os.path.basename(ruta) or ruta,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        guardar_favoritos(favs)
        if etiqueta_estrella is not None:
            try:
                etiqueta_estrella.configure(text="⭐", text_color=COLOR_AMARILLO)
            except Exception:
                pass
        mostrar_toast("⭐ Guardado en favoritos", COLOR_AMARILLO)


def guardar_busqueda_favorita():
    """Guarda la búsqueda actual (término + tipo + directorio) como favorita."""
    termino = entry_busqueda.get().strip()
    if not termino:
        mostrar_toast("⚠️ Escribe un término antes de guardar", COLOR_AMARILLO)
        return

    favs = cargar_favoritos()
    directorio = ("__TODOS_LOS_DISCOS__" if modo_todos_discos
                  else dir_busqueda.get().strip() or os.path.expanduser("~"))
    tipo = tipo_busqueda.get()

    for f in favs:
        if (f.get("tipo") == "busqueda" and f.get("termino") == termino
                and f.get("directorio") == directorio
                and f.get("tipo_busqueda") == tipo):
            mostrar_toast("ℹ️ Esa búsqueda ya está en favoritos", COLOR_ACENTO)
            return

    favs.append({
        "tipo": "busqueda",
        "termino": termino,
        "directorio": directorio,
        "tipo_busqueda": tipo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    guardar_favoritos(favs)
    mostrar_toast("⭐ Búsqueda guardada en favoritos", COLOR_AMARILLO)


def agregar_favorito_desde_explorador(tipo="carpeta"):
    """
    Abre el explorador del sistema para elegir una carpeta o archivo
    y lo añade como favorito.
    """
    if tipo == "carpeta":
        ruta = filedialog.askdirectory(title="Seleccionar carpeta favorita")
    else:
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo favorito",
            filetypes=[("Todos los archivos", "*.*")])

    if not ruta:
        return

    if es_favorito(ruta):
        mostrar_toast("ℹ️ Esa ruta ya está en favoritos", COLOR_ACENTO)
        return

    favs = cargar_favoritos()
    favs.append({
        "tipo": "ruta",
        "valor": ruta,
        "nombre": os.path.basename(ruta) or ruta,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    guardar_favoritos(favs)
    mostrar_toast("⭐ Añadido a favoritos", COLOR_AMARILLO)


def eliminar_favorito(indice):
    favs = cargar_favoritos()
    if 0 <= indice < len(favs):
        favs.pop(indice)
        guardar_favoritos(favs)
        mostrar_toast("🗑️ Favorito eliminado", COLOR_ROJO)


def aplicar_favorito_busqueda(fav):
    """Rellena la UI con los datos de una búsqueda favorita y la lanza."""
    global modo_todos_discos
    entry_busqueda.delete(0, "end")
    entry_busqueda.insert(0, fav.get("termino", ""))
    tipo_busqueda.set(fav.get("tipo_busqueda", "ambos"))

    directorio = fav.get("directorio", "")
    if directorio == "__TODOS_LOS_DISCOS__":
        seleccionar_todos_los_discos()
    else:
        modo_todos_discos = False
        entry_dir.delete(0, "end")
        entry_dir.insert(0, directorio)
        dir_busqueda.set(directorio)

    iniciar_busqueda()


# ============ VENTANAS DE FAVORITOS E HISTORIAL ============

def _crear_ventana_flotante(titulo, ancho=720, alto=560, color_titulo=COLOR_AMARILLO):
    win = ctk.CTkToplevel(ventana)
    win.title(titulo)
    win.geometry(f"{ancho}x{alto}")
    win.minsize(560, 400)
    win.configure(fg_color=COLOR_FONDO)
    win.transient(ventana)
    win.grab_set()

    cab = ctk.CTkFrame(win, fg_color=COLOR_FONDO_2, corner_radius=0)
    cab.pack(fill="x")
    ctk.CTkLabel(cab, text=titulo,
                 font=("Segoe UI", 18, "bold"),
                 text_color=color_titulo).pack(side="left", padx=18, pady=12)
    ctk.CTkButton(cab, text="✖ Cerrar",
                  command=win.destroy,
                  width=90, height=32,
                  fg_color=COLOR_ROJO, hover_color="#e07191",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 11, "bold")).pack(side="right", padx=12)

    cont = ctk.CTkScrollableFrame(win, fg_color=COLOR_FONDO,
                                  corner_radius=0)
    cont.pack(fill="both", expand=True, padx=14, pady=14)
    return win, cont


def abrir_panel_favoritos():
    win, cont = _crear_ventana_flotante("⭐ Favoritos", color_titulo=COLOR_AMARILLO)

    # --- Acciones ---
    acciones = ctk.CTkFrame(cont, fg_color=COLOR_FONDO_2, corner_radius=12)
    acciones.pack(fill="x", pady=(0, 12))

    ctk.CTkLabel(acciones, text="Acciones rápidas",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE).pack(anchor="w", padx=14, pady=(12, 6))

    fila_btn = ctk.CTkFrame(acciones, fg_color="transparent")
    fila_btn.pack(fill="x", padx=14, pady=(0, 14))

    ctk.CTkButton(fila_btn, text="⭐ Guardar búsqueda actual",
                  command=guardar_busqueda_favorita,
                  width=200, height=34,
                  fg_color=COLOR_AMARILLO, hover_color="#f5d78a",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 8))

    ctk.CTkButton(fila_btn, text="📁 Añadir carpeta favorita",
                  command=lambda: (agregar_favorito_desde_explorador("carpeta"),
                                   win.destroy(), abrir_panel_favoritos()),
                  width=200, height=34,
                  fg_color=COLOR_ACENTO, hover_color=COLOR_ACENTO_HOVER,
                  text_color="#1e1e2e",
                  font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 8))

    ctk.CTkButton(fila_btn, text="📄 Añadir archivo favorito",
                  command=lambda: (agregar_favorito_desde_explorador("archivo"),
                                   win.destroy(), abrir_panel_favoritos()),
                  width=200, height=34,
                  fg_color=COLOR_VERDE, hover_color="#8ed189",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 11, "bold")).pack(side="left")

    # --- Lista ---
    favs = cargar_favoritos()
    if not favs:
        ctk.CTkLabel(cont, text="Aún no tienes favoritos guardados.\n"
                                "Usa los botones de arriba, o el botón ⋮ de un resultado.",
                     font=("Segoe UI", 12),
                     text_color=COLOR_TEXTO_SUAVE,
                     justify="left").pack(anchor="w", padx=8, pady=20)
        return

    for i, fav in enumerate(favs):
        tipo = fav.get("tipo")
        card = ctk.CTkFrame(cont, fg_color=COLOR_FONDO_2, corner_radius=10,
                            border_width=1, border_color=COLOR_BORDE)
        card.pack(fill="x", pady=4, padx=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        if tipo == "busqueda":
            titulo = f"🔎  {fav.get('termino', '')}"
            dir_txt = fav.get("directorio", "")
            if dir_txt == "__TODOS_LOS_DISCOS__":
                dir_txt = "💽 Todos los discos"
            subt = f"📁 {dir_txt}   •   🎯 {fav.get('tipo_busqueda', 'ambos')}"
            ctk.CTkLabel(inner, text=titulo,
                         font=("Segoe UI", 13, "bold"),
                         text_color=COLOR_ACENTO,
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(inner, text=subt,
                         font=("Segoe UI", 11),
                         text_color=COLOR_TEXTO_SUAVE,
                         anchor="w").pack(anchor="w")

            botones = ctk.CTkFrame(inner, fg_color="transparent")
            botones.pack(anchor="e")
            ctk.CTkButton(botones, text="🔁 Buscar",
                          command=lambda f=fav: (win.destroy(), aplicar_favorito_busqueda(f)),
                          width=100, height=28,
                          fg_color=COLOR_ACENTO, hover_color=COLOR_ACENTO_HOVER,
                          text_color="#1e1e2e",
                          font=("Segoe UI", 11, "bold")).pack(side="left", padx=3)
            ctk.CTkButton(botones, text="🗑️",
                          command=lambda idx=i: (eliminar_favorito(idx), win.destroy(), abrir_panel_favoritos()),
                          width=40, height=28,
                          fg_color=COLOR_ROJO, hover_color="#e07191",
                          text_color="#1e1e2e",
                          font=("Segoe UI", 11, "bold")).pack(side="left", padx=3)

        elif tipo == "ruta":
            ruta = fav.get("valor", "")
            nombre = fav.get("nombre", os.path.basename(ruta))

            # ¿Existe y es archivo o carpeta? Si no existe, lo tratamos como archivo
            if os.path.exists(ruta):
                es_archivo = os.path.isfile(ruta)
            else:
                # Fallback: si la ruta no existe, no sabemos. Mostramos como archivo
                # (los botones siguen funcionando en el sentido de "abrir").
                es_archivo = True

            icono, color = obtener_icono_y_color(ruta, es_archivo)
            ctk.CTkLabel(inner, text=f"{icono}  {nombre}",
                         font=("Segoe UI", 13, "bold"),
                         text_color=color,
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(inner, text=ruta,
                         font=("Segoe UI", 10),
                         text_color=COLOR_TEXTO_SUAVE,
                         anchor="w").pack(anchor="w")

            botones = ctk.CTkFrame(inner, fg_color="transparent")
            botones.pack(anchor="e")

            # Archivo → Abrir + Carpeta contenedora
            # Carpeta → Abrir carpeta (un único botón)
            if es_archivo:
                ctk.CTkButton(botones, text="🚀 Abrir",
                              command=lambda r=ruta: abrir_archivo(r),
                              width=90, height=28,
                              fg_color=COLOR_ACENTO, hover_color=COLOR_ACENTO_HOVER,
                              text_color="#1e1e2e",
                              font=("Segoe UI", 11, "bold")).pack(side="left", padx=3)
                ctk.CTkButton(botones, text="📁 Carpeta contenedora",
                              command=lambda r=ruta: abrir_carpeta_contenedora(r),
                              width=150, height=28,
                              fg_color=COLOR_VERDE, hover_color="#8ed189",
                              text_color="#1e1e2e",
                              font=("Segoe UI", 11, "bold")).pack(side="left", padx=3)
            else:
                ctk.CTkButton(botones, text="📂 Abrir carpeta",
                              command=lambda r=ruta: abrir_archivo(r),
                              width=130, height=28,
                              fg_color=COLOR_ACENTO, hover_color=COLOR_ACENTO_HOVER,
                              text_color="#1e1e2e",
                              font=("Segoe UI", 11, "bold")).pack(side="left", padx=3)

            ctk.CTkButton(botones, text="🗑️",
                          command=lambda idx=i: (eliminar_favorito(idx), win.destroy(), abrir_panel_favoritos()),
                          width=40, height=28,
                          fg_color=COLOR_ROJO, hover_color="#e07191",
                          text_color="#1e1e2e",
                          font=("Segoe UI", 11, "bold")).pack(side="left", padx=3)


def borrar_historial():
    """Borra el historial (con confirmación). Pregunta si borrar todo o solo hoy."""
    resp = messagebox.askyesnocancel(
        "Borrar historial",
        "¿Quieres borrar TODO el historial?\n\n"
        "Sí  → borrar todo el historial\n"
        "No  → borrar solo el de HOY\n"
        "Cancelar → no hacer nada")

    if resp is None:
        return
    if resp:
        guardar_historial([])
        mostrar_toast("🗑️ Historial completo borrado", COLOR_ROJO)
    else:
        hoy = date.today().strftime("%Y-%m-%d")
        hist = [h for h in cargar_historial() if h.get("fecha") != hoy]
        guardar_historial(hist)
        mostrar_toast("🗑️ Historial de hoy borrado", COLOR_ROJO)


def abrir_panel_historial():
    win, cont = _crear_ventana_flotante("🕘 Historial de hoy", color_titulo=COLOR_MORADO)

    # --- Acciones ---
    acciones = ctk.CTkFrame(cont, fg_color=COLOR_FONDO_2, corner_radius=12)
    acciones.pack(fill="x", pady=(0, 12))

    ctk.CTkLabel(acciones, text="Acciones",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE).pack(anchor="w", padx=14, pady=(12, 6))

    ctk.CTkButton(acciones, text="🗑️ Borrar historial",
                  command=lambda: (borrar_historial(), win.destroy(),
                                   abrir_panel_historial()),
                  width=200, height=34,
                  fg_color=COLOR_ROJO, hover_color="#e07191",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(0, 14))

    hist_hoy = historial_de_hoy()
    hist_hoy.reverse()  # más reciente primero

    if not hist_hoy:
        ctk.CTkLabel(cont,
                     text="No hay búsquedas registradas hoy.\n"
                          "Cada búsqueda que realices se guardará aquí automáticamente.",
                     font=("Segoe UI", 12),
                     text_color=COLOR_TEXTO_SUAVE,
                     justify="left").pack(anchor="w", padx=8, pady=20)
        return

    ctk.CTkLabel(cont,
                 text=f"Se muestran las {len(hist_hoy)} búsquedas de hoy:",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE).pack(anchor="w", padx=8, pady=(0, 8))

    for h in hist_hoy:
        card = ctk.CTkFrame(cont, fg_color=COLOR_FONDO_2, corner_radius=10,
                            border_width=1, border_color=COLOR_BORDE)
        card.pack(fill="x", pady=4, padx=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(inner,
                     text=f"🕐 {h.get('hora', '--:--:--')}   •   🔎 {h.get('termino', '')}",
                     font=("Segoe UI", 13, "bold"),
                     text_color=COLOR_ACENTO,
                     anchor="w").pack(anchor="w")

        dir_txt = h.get("directorio", "")
        if dir_txt == "__TODOS_LOS_DISCOS__":
            dir_txt = "💽 Todos los discos"
        ctk.CTkLabel(inner,
                     text=f"📁 {dir_txt}   •   🎯 {h.get('tipo', 'ambos')}   •   "
                          f"📊 {h.get('resultados', 0)} resultados",
                     font=("Segoe UI", 11),
                     text_color=COLOR_TEXTO_SUAVE,
                     anchor="w").pack(anchor="w")

        ctk.CTkButton(inner, text="🔁 Repetir búsqueda",
                      command=lambda e=h: (win.destroy(), aplicar_historial(e)),
                      width=160, height=28,
                      fg_color=COLOR_MORADO, hover_color="#b18ef0",
                      text_color="#1e1e2e",
                      font=("Segoe UI", 11, "bold")).pack(anchor="e", pady=(4, 0))


def aplicar_historial(entrada):
    """Reaplica una búsqueda guardada en el historial."""
    global modo_todos_discos
    entry_busqueda.delete(0, "end")
    entry_busqueda.insert(0, entrada.get("termino", ""))
    tipo_busqueda.set(entrada.get("tipo", "ambos"))

    directorio = entrada.get("directorio", "")
    if directorio == "__TODOS_LOS_DISCOS__":
        seleccionar_todos_los_discos()
    else:
        modo_todos_discos = False
        entry_dir.delete(0, "end")
        entry_dir.insert(0, directorio)
        dir_busqueda.set(directorio)

    iniciar_busqueda()


# ============ PANEL AVANZADO (FILTRO DE EXTENSIONES) ============

def _pasa_filtro_extension(ruta, es_archivo):
    """Devuelve True si la ruta pasa el filtro de extensiones."""
    if not filtro_extensiones_activo:
        return True
    if not es_archivo:
        return True
    ext = os.path.splitext(ruta)[1].lower()
    return ext in extensiones_seleccionadas


def _actualizar_estado_filtro():
    """Recalcula filtro_extensiones_activo según las extensiones marcadas."""
    global filtro_extensiones_activo
    filtro_extensiones_activo = len(extensiones_seleccionadas) > 0
    if label_filtro_estado is not None:
        label_filtro_estado.configure(
            text=(f"🔎 Filtro activo: {len(extensiones_seleccionadas)} extensiones"
                  if filtro_extensiones_activo
                  else "Sin filtro (se muestran todas las extensiones)"),
            text_color=COLOR_VERDE if filtro_extensiones_activo else COLOR_TEXTO_SUAVE,
        )


def _toggle_extension(ext, var):
    if var.get():
        extensiones_seleccionadas.add(ext)
    else:
        extensiones_seleccionadas.discard(ext)
    _actualizar_estado_filtro()


def _toggle_categoria(categoria, marcar):
    """Marca o desmarca todas las extensiones de una categoría."""
    datos = TIPOS_ARCHIVO[categoria]
    for ext in datos['ext']:
        var = _vars_extensiones.get(ext)
        if var is None:
            continue
        if var.get() != marcar:
            var.set(marcar)
        if marcar:
            extensiones_seleccionadas.add(ext)
        else:
            extensiones_seleccionadas.discard(ext)
    _actualizar_estado_filtro()


def _limpiar_filtros():
    global extensiones_seleccionadas
    extensiones_seleccionadas.clear()
    for var in _vars_extensiones.values():
        var.set(False)
    _actualizar_estado_filtro()
    mostrar_toast("🧹 Filtros limpiados", COLOR_VERDE)


def toggle_panel_avanzado():
    """Muestra u oculta el panel de filtros avanzados."""
    global panel_avanzado_visible
    if panel_avanzado is None:
        return

    if panel_avanzado_visible:
        panel_avanzado.pack_forget()
        panel_avanzado_visible = False
        if btn_avanzado is not None:
            btn_avanzado.configure(fg_color=COLOR_MORADO)
        return

    panel_avanzado_visible = True
    if btn_avanzado is not None:
        btn_avanzado.configure(fg_color=COLOR_ACENTO)
    panel_avanzado.pack(fill="x", padx=24, pady=(0, 12), after=opciones)


def crear_panel_avanzado(parent):
    """Construye el panel de filtros avanzados (oculto por defecto)."""
    global panel_avanzado, label_filtro_estado

    panel = ctk.CTkFrame(parent, fg_color=COLOR_FONDO_2, corner_radius=14)

    cab = ctk.CTkFrame(panel, fg_color="transparent")
    cab.pack(fill="x", padx=14, pady=(12, 4))

    ctk.CTkLabel(cab, text="⚙️  Filtro por extensión",
                 font=("Segoe UI", 14, "bold"),
                 text_color=COLOR_MORADO).pack(side="left")

    label_filtro_estado = ctk.CTkLabel(cab, text="",
                                       font=("Segoe UI", 11),
                                       text_color=COLOR_TEXTO_SUAVE)
    label_filtro_estado.pack(side="right")

    botones_globales = ctk.CTkFrame(panel, fg_color="transparent")
    botones_globales.pack(fill="x", padx=14, pady=(0, 8))

    ctk.CTkButton(botones_globales, text="🧹 Limpiar filtros",
                  command=_limpiar_filtros,
                  width=140, height=30,
                  fg_color=COLOR_ROJO, hover_color="#e07191",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 6))

    scroll_frame = ctk.CTkScrollableFrame(panel, height=220,
                                          fg_color=COLOR_FONDO_3,
                                          corner_radius=10)
    scroll_frame.pack(fill="x", padx=14, pady=(0, 12))

    for categoria, datos in TIPOS_ARCHIVO.items():
        cat_frame = ctk.CTkFrame(scroll_frame, fg_color=COLOR_FONDO_2,
                                 corner_radius=8)
        cat_frame.pack(fill="x", pady=3, padx=2)

        cab_cat = ctk.CTkFrame(cat_frame, fg_color="transparent")
        cab_cat.pack(fill="x", padx=8, pady=(6, 2))

        ctk.CTkLabel(cab_cat,
                     text=f"{datos['icono']}  {categoria.capitalize()}",
                     font=("Segoe UI", 12, "bold"),
                     text_color=datos['color']).pack(side="left")

        ctk.CTkButton(cab_cat, text="Todo",
                      command=lambda c=categoria: _toggle_categoria(c, True),
                      width=52, height=22,
                      fg_color=datos['color'], hover_color=datos['color'],
                      text_color="#1e1e2e",
                      font=("Segoe UI", 10, "bold")).pack(side="right", padx=(4, 0))
        ctk.CTkButton(cab_cat, text="Nada",
                      command=lambda c=categoria: _toggle_categoria(c, False),
                      width=52, height=22,
                      fg_color=COLOR_BORDE, hover_color="#5a5c70",
                      text_color=COLOR_TEXTO,
                      font=("Segoe UI", 10, "bold")).pack(side="right")

        grid = ctk.CTkFrame(cat_frame, fg_color="transparent")
        grid.pack(fill="x", padx=8, pady=(0, 8))

        columnas = 6
        for i, ext in enumerate(datos['ext']):
            var = tk.BooleanVar(value=(ext in extensiones_seleccionadas))
            _vars_extensiones[ext] = var

            cb = ctk.CTkCheckBox(
                grid,
                text=ext,
                variable=var,
                command=lambda e=ext, v=var: _toggle_extension(e, v),
                font=("Segoe UI", 10),
                text_color=COLOR_TEXTO,
                fg_color=datos['color'],
                hover_color=datos['color'],
                border_color=COLOR_BORDE,
                checkbox_width=16,
                checkbox_height=16,
            )
            cb.grid(row=i // columnas, column=i % columnas,
                    padx=4, pady=2, sticky="w")

    panel_avanzado = panel
    _actualizar_estado_filtro()
    return panel


# ============ BÚSQUEDA ============

def iniciar_busqueda():
    global busqueda_activa, modo_todos_discos
    if busqueda_activa:
        return

    texto_buscar = entry_busqueda.get().strip()
    if not texto_buscar:
        mostrar_toast("⚠️ Ingresa un término de búsqueda", COLOR_AMARILLO)
        return

    if modo_todos_discos:
        directorios = obtener_unidades()
        if not directorios:
            mostrar_toast("❌ No se detectaron discos", COLOR_ROJO)
            return
        directorio_hist = "__TODOS_LOS_DISCOS__"
    else:
        directorio = dir_busqueda.get().strip()
        if not directorio or not os.path.exists(directorio):
            mostrar_toast("❌ El directorio no existe", COLOR_ROJO)
            return
        directorios = [directorio]
        directorio_hist = directorio

    limpiar_resultados()

    label_estado.configure(text="⏳ Buscando...", text_color=COLOR_AMARILLO)
    label_info.configure(text="")
    btn_buscar.configure(state="disabled", fg_color=COLOR_BORDE)
    btn_detener.configure(state="normal", fg_color=COLOR_ROJO)

    tipo = tipo_busqueda.get()
    max_res = max_resultados_var.get().strip()
    max_res = int(max_res) if max_res.isdigit() else None

    busqueda_activa = True
    hilo = Thread(target=ejecutar_busqueda,
                  args=(directorios, texto_buscar, tipo, max_res,
                        directorio_hist),
                  daemon=True)
    hilo.start()


def ejecutar_busqueda(directorios, patron, tipo, max_resultados,
                      directorio_hist):
    try:
        resultados = []
        inicio = time.time()

        for directorio in directorios:
            if not busqueda_activa:
                break

            restante = None
            if max_resultados:
                restante = max_resultados - len(resultados)
                if restante <= 0:
                    break

            if patron.startswith('*') or '?' in patron:
                parciales = buscar_con_comodines(
                    directorio, patron, tipo, restante)
            else:
                if tipo == "archivos":
                    parciales = buscar_archivos_por_nombre(
                        directorio, patron, restante)
                elif tipo == "carpetas":
                    parciales = buscar_carpetas_por_nombre(
                        directorio, patron, restante)
                else:
                    completos, _t = buscar_completo(
                        directorio, patron, tipo, restante)
                    parciales = completos['archivos'] + completos['carpetas']

            resultados.extend(parciales)

            if max_resultados and len(resultados) >= max_resultados:
                resultados = resultados[:max_resultados]
                break

        tiempo_total = time.time() - inicio

        try:
            agregar_al_historial(patron, tipo, directorio_hist, len(resultados))
        except Exception:
            pass

        ventana.after(0, mostrar_resultados_en_gui,
                      resultados, tiempo_total, patron)
    except Exception as e:
        ventana.after(0, mostrar_error, str(e))


def mostrar_resultados_en_gui(resultados, tiempo, patron):
    global busqueda_activa
    busqueda_activa = False
    btn_buscar.configure(state="normal", fg_color=COLOR_ACENTO)
    btn_detener.configure(state="disabled", fg_color=COLOR_BORDE)

    if not resultados:
        label_estado.configure(text="❌ Sin resultados", text_color=COLOR_ROJO)
        mostrar_toast(f"Sin resultados para '{patron}'", COLOR_ROJO)
        return

    archivos, carpetas = [], []
    total_brutos = len(resultados)

    for ruta in resultados:
        if not os.path.exists(ruta):
            continue
        es_archivo = os.path.isfile(ruta)

        if not _pasa_filtro_extension(ruta, es_archivo):
            continue

        if es_archivo:
            archivos.append(ruta)
            mostrar_resultado(ruta, True)
        else:
            carpetas.append(ruta)
            mostrar_resultado(ruta, False)

    total_filtrado = len(archivos) + len(carpetas)

    if total_filtrado == 0:
        label_estado.configure(
            text="⚠️ Resultados filtrados a 0", text_color=COLOR_AMARILLO)
        label_info.configure(
            text=f"🔎 {total_brutos} encontrados, 0 visibles por el filtro de extensiones")
        mostrar_toast("Ningún resultado pasa el filtro de extensiones", COLOR_AMARILLO)
        return

    texto_estado = f"✅ Completado en {tiempo:.2f} s"
    if filtro_extensiones_activo:
        texto_estado += "  ·  🔎 filtro activo"
    label_estado.configure(text=texto_estado, text_color=COLOR_VERDE)

    texto_info = (
        f"📊 {total_filtrado} resultados   •   "
        f"📄 {len(archivos)} archivos   •   📁 {len(carpetas)} carpetas"
    )
    if filtro_extensiones_activo and total_brutos != total_filtrado:
        texto_info += f"   (de {total_brutos} encontrados)"
    label_info.configure(text=texto_info)
    on_frame_configure()


def mostrar_error(mensaje):
    global busqueda_activa
    busqueda_activa = False
    btn_buscar.configure(state="normal", fg_color=COLOR_ACENTO)
    btn_detener.configure(state="disabled", fg_color=COLOR_BORDE)
    label_estado.configure(text="❌ Error en la búsqueda", text_color=COLOR_ROJO)
    messagebox.showerror("Error", f"Error durante la búsqueda:\n{mensaje}")


def detener_busqueda():
    global busqueda_activa
    if busqueda_activa:
        busqueda_activa = False
        label_estado.configure(text="⏹ Búsqueda detenida", text_color=COLOR_AMARILLO)
        btn_buscar.configure(state="normal", fg_color=COLOR_ACENTO)
        btn_detener.configure(state="disabled", fg_color=COLOR_BORDE)


# ============ INTERFAZ ============

def crear_interfaz():
    global ventana, entry_busqueda, entry_dir, entry_max, tipo_busqueda
    global dir_busqueda, max_resultados_var, label_estado, label_info
    global btn_buscar, btn_detener, frame_resultados, canvas_resultados
    global btn_avanzado, opciones

    ventana = ctk.CTk()
    ventana.title("🔍 Buscador de Archivos")
    ventana.geometry("1000x760")
    ventana.minsize(760, 560)
    ventana.configure(fg_color=COLOR_FONDO)

    try:
        icono1 = Image.open("./img/icono1.png")
        icono_ventana = ImageTk.PhotoImage(icono1)
        ventana.iconphoto(False, icono_ventana)
    except Exception:
        pass

    # ---------- HEADER ----------
    header = ctk.CTkFrame(ventana, fg_color="transparent")
    header.pack(fill="x", padx=24, pady=(20, 6))

    ctk.CTkLabel(header,
                 text="🔍  Buscador de Archivos",
                 font=("Segoe UI", 26, "bold"),
                 text_color=COLOR_ACENTO).pack(side="left")

    ctk.CTkLabel(header,
                 text="Encuentra lo que buscas, rápido y bonito",
                 font=("Segoe UI", 12),
                 text_color=COLOR_TEXTO_SUAVE).pack(side="left", padx=14, pady=(8, 0))

    btn_avanzado = ctk.CTkButton(header,
                                 text="⚙️ Avanzado",
                                 command=toggle_panel_avanzado,
                                 width=130, height=36,
                                 corner_radius=10,
                                 fg_color=COLOR_MORADO,
                                 hover_color="#b18ef0",
                                 text_color="#1e1e2e",
                                 font=("Segoe UI", 12, "bold"))
    btn_avanzado.pack(side="right")

    ctk.CTkButton(header,
                  text="⭐ Favoritos",
                  command=abrir_panel_favoritos,
                  width=130, height=36,
                  corner_radius=10,
                  fg_color=COLOR_AMARILLO,
                  hover_color="#f5d78a",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 12, "bold")).pack(side="right", padx=(0, 8))

    ctk.CTkButton(header,
                  text="🕘 Historial",
                  command=abrir_panel_historial,
                  width=130, height=36,
                  corner_radius=10,
                  fg_color=COLOR_MORADO,
                  hover_color="#b18ef0",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 12, "bold")).pack(side="right", padx=(0, 8))

    # ---------- BARRA DE BÚSQUEDA ----------
    barra = ctk.CTkFrame(ventana, fg_color=COLOR_FONDO_2, corner_radius=14)
    barra.pack(fill="x", padx=24, pady=14)

    fila_busqueda = ctk.CTkFrame(barra, fg_color="transparent")
    fila_busqueda.pack(fill="x", padx=14, pady=12)

    entry_busqueda = ctk.CTkEntry(fila_busqueda,
                                  placeholder_text="Escribe el nombre o patrón (*.mp4, foto*, etc.)",
                                  height=42,
                                  corner_radius=10,
                                  fg_color=COLOR_FONDO_3,
                                  border_color=COLOR_BORDE,
                                  text_color=COLOR_TEXTO,
                                  font=("Segoe UI", 13))
    entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 10))
    entry_busqueda.bind("<Return>", lambda e: iniciar_busqueda())

    btn_buscar = ctk.CTkButton(fila_busqueda,
                               text="🔍 Buscar",
                               command=iniciar_busqueda,
                               width=120, height=42,
                               corner_radius=10,
                               fg_color=COLOR_ACENTO,
                               hover_color=COLOR_ACENTO_HOVER,
                               text_color="#1e1e2e",
                               font=("Segoe UI", 13, "bold"))
    btn_buscar.pack(side="left", padx=3)

    btn_detener = ctk.CTkButton(fila_busqueda,
                                text="⏹ Detener",
                                command=detener_busqueda,
                                width=110, height=42,
                                corner_radius=10,
                                fg_color=COLOR_BORDE,
                                hover_color="#5a5c70",
                                text_color=COLOR_TEXTO,
                                state="disabled",
                                font=("Segoe UI", 13, "bold"))
    btn_detener.pack(side="left", padx=3)

    # ---------- OPCIONES ----------
    opciones = ctk.CTkFrame(ventana, fg_color=COLOR_FONDO_2, corner_radius=14)
    opciones.pack(fill="x", padx=24, pady=(0, 12))

    fila_tipo = ctk.CTkFrame(opciones, fg_color="transparent")
    fila_tipo.pack(fill="x", padx=14, pady=(12, 4))

    ctk.CTkLabel(fila_tipo, text="Tipo:",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE).pack(side="left", padx=(0, 10))

    tipo_busqueda = tk.StringVar(value="ambos")

    for texto, valor in [("Archivos y carpetas", "ambos"),
                         ("Solo archivos", "archivos"),
                         ("Solo carpetas", "carpetas")]:
        ctk.CTkRadioButton(fila_tipo,
                           text=texto,
                           variable=tipo_busqueda,
                           value=valor,
                           fg_color=COLOR_ACENTO,
                           hover_color=COLOR_ACENTO_HOVER,
                           text_color=COLOR_TEXTO,
                           font=("Segoe UI", 12)).pack(side="left", padx=8)

    fila_dir = ctk.CTkFrame(opciones, fg_color="transparent")
    fila_dir.pack(fill="x", padx=14, pady=6)

    ctk.CTkLabel(fila_dir, text="Directorio:",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE,
                 width=90, anchor="w").pack(side="left")

    dir_busqueda = tk.StringVar(value=os.path.expanduser("~"))

    entry_dir = ctk.CTkEntry(fila_dir,
                             height=36,
                             corner_radius=10,
                             fg_color=COLOR_FONDO_3,
                             border_color=COLOR_BORDE,
                             text_color=COLOR_TEXTO,
                             font=("Segoe UI", 12))
    entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 8))
    entry_dir.insert(0, os.path.expanduser("~"))
    entry_dir.bind("<KeyRelease>", _on_dir_escrito)

    ctk.CTkButton(fila_dir,
                  text="📁 Examinar",
                  command=seleccionar_directorio,
                  width=110, height=36,
                  corner_radius=10,
                  fg_color=COLOR_ACENTO,
                  hover_color=COLOR_ACENTO_HOVER,
                  text_color="#1e1e2e",
                  font=("Segoe UI", 12, "bold")).pack(side="left")

    ctk.CTkButton(fila_dir,
                  text="💽 Todos los discos",
                  command=seleccionar_todos_los_discos,
                  width=150, height=36,
                  corner_radius=10,
                  fg_color=COLOR_MORADO,
                  hover_color="#b18ef0",
                  text_color="#1e1e2e",
                  font=("Segoe UI", 12, "bold")).pack(side="left", padx=(8, 0))

    fila_max = ctk.CTkFrame(opciones, fg_color="transparent")
    fila_max.pack(fill="x", padx=14, pady=(4, 12))

    ctk.CTkLabel(fila_max, text="Máx resultados:",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE,
                 width=120, anchor="w").pack(side="left")

    max_resultados_var = tk.StringVar(value="500")
    entry_max = ctk.CTkEntry(fila_max,
                             textvariable=max_resultados_var,
                             width=120, height=36,
                             corner_radius=10,
                             fg_color=COLOR_FONDO_3,
                             border_color=COLOR_BORDE,
                             text_color=COLOR_TEXTO,
                             font=("Segoe UI", 12),
                             placeholder_text="Sin límite")
    entry_max.pack(side="left", padx=(0, 10))

    ctk.CTkLabel(fila_max,
                 text="(vacío = sin límite · recomendado 1000 al buscar en todos los discos)",
                 font=("Segoe UI", 11),
                 text_color=COLOR_TEXTO_SUAVE).pack(side="left")

    crear_panel_avanzado(ventana)

    # ---------- ESTADO ----------
    estado_frame = ctk.CTkFrame(ventana, fg_color="transparent")
    estado_frame.pack(fill="x", padx=26, pady=(0, 4))

    label_estado = ctk.CTkLabel(estado_frame,
                                text="✅ Listo",
                                font=("Segoe UI", 13, "bold"),
                                text_color=COLOR_VERDE)
    label_estado.pack(side="left")

    label_info = ctk.CTkLabel(estado_frame,
                              text="",
                              font=("Segoe UI", 12),
                              text_color=COLOR_TEXTO_SUAVE)
    label_info.pack(side="right")

    # ---------- RESULTADOS ----------
    resultados_frame = ctk.CTkFrame(ventana, fg_color=COLOR_FONDO_2, corner_radius=14)
    resultados_frame.pack(fill="both", expand=True, padx=24, pady=(8, 20))

    ctk.CTkLabel(resultados_frame,
                 text="  Resultados (usa el botón ⋮ para opciones)",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE,
                 anchor="w").pack(fill="x", padx=12, pady=(10, 0))

    contenedor_scroll = ctk.CTkFrame(resultados_frame, fg_color="transparent")
    contenedor_scroll.pack(fill="both", expand=True, padx=8, pady=8)

    canvas_resultados = tk.Canvas(contenedor_scroll,
                                  bg=COLOR_FONDO_2,
                                  highlightthickness=0,
                                  bd=0)
    canvas_resultados.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(contenedor_scroll,
                                 command=canvas_resultados.yview,
                                 fg_color=COLOR_FONDO_2,
                                 button_color=COLOR_ACENTO,
                                 button_hover_color=COLOR_ACENTO_HOVER)
    scrollbar.pack(side="right", fill="y")
    canvas_resultados.configure(yscrollcommand=scrollbar.set)

    frame_resultados = ctk.CTkFrame(canvas_resultados, fg_color=COLOR_FONDO_2)
    canvas_resultados.create_window((0, 0), window=frame_resultados,
                                    anchor="nw", width=900)

    frame_resultados.bind("<Configure>", on_frame_configure)
    canvas_resultados.bind("<Configure>", on_canvas_configure)

    ventana.bind("<Control-f>", lambda e: entry_busqueda.focus())
    ventana.bind("<Control-F>", lambda e: entry_busqueda.focus())

    centrar_ventana()
    return ventana


# ============ MAIN ============

def main():
    global ventana
    ventana = crear_interfaz()
    ventana.mainloop()


if __name__ == "__main__":
    main()
