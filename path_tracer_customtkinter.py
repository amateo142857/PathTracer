import os
import time
import subprocess
import fnmatch
import platform
import tkinter as tk
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
                '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg'],
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


# ============ FUNCIONES DEL BUSCADOR ============

def buscar_completo(directorio, patron, tipo="ambos", max_resultados=None):
    resultados = {'archivos': [], 'carpetas': [], 'total': 0}
    contador = 0
    inicio = time.time()

    for root, dirs, files in os.walk(directorio):
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


def buscar_con_comodines(directorio, patron, tipo="ambos"):
    resultados = []
    for root, dirs, files in os.walk(directorio):
        if tipo in ["archivos", "ambos"]:
            for archivo in files:
                if fnmatch.fnmatch(archivo.lower(), patron.lower()):
                    resultados.append(os.path.join(root, archivo))
        if tipo in ["carpetas", "ambos"]:
            for carpeta in dirs:
                if fnmatch.fnmatch(carpeta.lower(), patron.lower()):
                    resultados.append(os.path.join(root, carpeta))
    return resultados


def buscar_carpetas_por_nombre(directorio, patron):
    resultados = []
    for root, dirs, _ in os.walk(directorio):
        for carpeta in dirs:
            if patron.lower() in carpeta.lower():
                resultados.append(os.path.join(root, carpeta))
    return resultados


def buscar_archivos_por_nombre(directorio, patron, max_resultados=None):
    resultados = []
    contador = 0
    for root, _, files in os.walk(directorio):
        if max_resultados and contador >= max_resultados:
            break
        for archivo in files:
            if patron.lower() in archivo.lower():
                resultados.append(os.path.join(root, archivo))
                contador += 1
                if max_resultados and contador >= max_resultados:
                    break
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
        mostrar_toast(f"📋 Ruta copiada", COLOR_VERDE)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar:\n{str(e)}")


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
        except:
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
    except:
        pass


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
    directorio = filedialog.askdirectory(title="Seleccionar directorio de búsqueda")
    if directorio:
        dir_busqueda.set(directorio)
        entry_dir.delete(0, "end")
        entry_dir.insert(0, directorio)


def limpiar_resultados():
    global frame_resultados
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    label_info.configure(text="")


def mostrar_resultado(ruta, es_archivo):
    nombre = os.path.basename(ruta)
    icono, color = obtener_icono_y_color(ruta, es_archivo)

    # Tarjeta
    card = ctk.CTkFrame(frame_resultados,
                        fg_color=COLOR_FONDO_2,
                        corner_radius=10,
                        border_width=1,
                        border_color=COLOR_BORDE)
    card.pack(fill="x", pady=4, padx=4)

    # Contenedor horizontal interno
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=10, pady=8)

    # Icono + nombre (a la izquierda)
    label_nombre = ctk.CTkLabel(inner,
                                text=f"{icono}  {nombre}",
                                text_color=color,
                                font=("Segoe UI", 13, "bold"),
                                anchor="w")
    label_nombre.pack(side="left", fill="x", expand=True)

    # Tooltip con ruta completa
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
            card.tooltip.destroy()

    label_nombre.bind("<Enter>", mostrar_tooltip)
    label_nombre.bind("<Leave>", ocultar_tooltip)

    # Botones (a la derecha)
    btn_container = ctk.CTkFrame(inner, fg_color="transparent")
    btn_container.pack(side="right")

    def crear_boton(texto, comando, color_hover=COLOR_ACENTO_HOVER):
        return ctk.CTkButton(btn_container,
                             text=texto,
                             command=comando,
                             width=90, height=28,
                             corner_radius=8,
                             fg_color=COLOR_ACENTO,
                             hover_color=color_hover,
                             text_color="#1e1e2e",
                             font=("Segoe UI", 10, "bold"))

    btn_abrir = crear_boton("🚀 Abrir", lambda: abrir_archivo(ruta))
    btn_abrir.pack(side="left", padx=3)

    btn_carpeta = crear_boton("📂 Carpeta", lambda: abrir_carpeta_contenedora(ruta))
    btn_carpeta.pack(side="left", padx=3)

    btn_copiar = crear_boton("📋 Copiar", lambda: copiar_ruta_al_portapapeles(ruta))
    btn_copiar.pack(side="left", padx=3)

    btn_info = crear_boton("ℹ️ Info", lambda: mostrar_info(ruta), COLOR_MORADO)
    btn_info.pack(side="left", padx=3)


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
        except:
            info += "📊 Contenido: No accesible\n"
    messagebox.showinfo(f"Información: {nombre}", info)


# ============ BÚSQUEDA ============

def iniciar_busqueda():
    global busqueda_activa
    if busqueda_activa:
        return

    texto_buscar = entry_busqueda.get().strip()
    if not texto_buscar:
        mostrar_toast("⚠️ Ingresa un término de búsqueda", COLOR_AMARILLO)
        return

    directorio = dir_busqueda.get().strip()
    if not os.path.exists(directorio):
        mostrar_toast("❌ El directorio no existe", COLOR_ROJO)
        return

    limpiar_resultados()

    label_estado.configure(text="⏳ Buscando...", text_color=COLOR_AMARILLO)
    label_info.configure(text="")
    btn_buscar.configure(state="disabled", fg_color=COLOR_BORDE)
    btn_detener.configure(state="normal", fg_color=COLOR_ROJO)

    tipo = tipo_busqueda.get()
    max_res = max_resultados_var.get().strip()
    max_res = int(max_res) if max_res else None

    busqueda_activa = True
    hilo = Thread(target=ejecutar_busqueda,
                  args=(directorio, texto_buscar, tipo, max_res),
                  daemon=True)
    hilo.start()


def ejecutar_busqueda(directorio, patron, tipo, max_resultados):
    try:
        resultados = []
        tiempo = 0

        if patron.startswith('*') or '?' in patron:
            resultados = buscar_con_comodines(directorio, patron, tipo)
        else:
            if tipo == "archivos":
                resultados = buscar_archivos_por_nombre(directorio, patron, max_resultados)
            elif tipo == "carpetas":
                resultados = buscar_carpetas_por_nombre(directorio, patron)
            else:
                completos, tiempo = buscar_completo(directorio, patron, tipo, max_resultados)
                resultados = completos['archivos'] + completos['carpetas']

        if max_resultados and len(resultados) > max_resultados:
            resultados = resultados[:max_resultados]

        ventana.after(0, mostrar_resultados_en_gui, resultados, tiempo, patron)
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
    for ruta in resultados:
        if os.path.exists(ruta):
            if os.path.isfile(ruta):
                archivos.append(ruta)
            else:
                carpetas.append(ruta)
            mostrar_resultado(ruta, os.path.isfile(ruta))

    label_estado.configure(
        text=f"✅ Completado en {tiempo:.2f} s",
        text_color=COLOR_VERDE)
    label_info.configure(
        text=f"📊 {len(resultados)} resultados   •   "
             f"📄 {len(archivos)} archivos   •   📁 {len(carpetas)} carpetas")
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

    ventana = ctk.CTk()
    ventana.title("🔍 Buscador de Archivos")
    ventana.geometry("1000x760")
    ventana.minsize(760, 560)
    ventana.configure(fg_color=COLOR_FONDO)

    # Icono
    try:
        icono1 = Image.open("./img/icono1.png")
        icono_ventana = ImageTk.PhotoImage(icono1)
        ventana.iconphoto(False, icono_ventana)
    except:
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

    # Fila: Tipo
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

    # Fila: Directorio
    fila_dir = ctk.CTkFrame(opciones, fg_color="transparent")
    fila_dir.pack(fill="x", padx=14, pady=6)

    ctk.CTkLabel(fila_dir, text="Directorio:",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE,
                 width=90, anchor="w").pack(side="left")

    dir_busqueda = tk.StringVar(value=os.path.expanduser("~"))
    entry_dir = ctk.CTkEntry(fila_dir,
                             textvariable=dir_busqueda,
                             height=36,
                             corner_radius=10,
                             fg_color=COLOR_FONDO_3,
                             border_color=COLOR_BORDE,
                             text_color=COLOR_TEXTO,
                             font=("Segoe UI", 12))
    entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 8))

    ctk.CTkButton(fila_dir,
                  text="📁 Examinar",
                  command=seleccionar_directorio,
                  width=110, height=36,
                  corner_radius=10,
                  fg_color=COLOR_ACENTO,
                  hover_color=COLOR_ACENTO_HOVER,
                  text_color="#1e1e2e",
                  font=("Segoe UI", 12, "bold")).pack(side="left")

    # Fila: Máx resultados
    fila_max = ctk.CTkFrame(opciones, fg_color="transparent")
    fila_max.pack(fill="x", padx=14, pady=(4, 12))

    ctk.CTkLabel(fila_max, text="Máx resultados:",
                 font=("Segoe UI", 12, "bold"),
                 text_color=COLOR_TEXTO_SUAVE,
                 width=120, anchor="w").pack(side="left")

    max_resultados_var = tk.StringVar(value="")
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

    ctk.CTkLabel(fila_max, text="(vacío = sin límite)",
                 font=("Segoe UI", 11),
                 text_color=COLOR_TEXTO_SUAVE).pack(side="left")

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
                 text="  Resultados",
                 font=("Segoe UI", 13, "bold"),
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

    # Atajos
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