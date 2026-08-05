import os
import sys
import time
import subprocess
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from threading import Thread
import platform
from PIL import Image, ImageTk

# ============ CONFIGURACIÓN DE COLORES (¡CAMBIA AQUÍ!) ============

# --- Colores de la ventana ---
COLOR_VENTANA = "#1e1e1e"          # Fondo principal
COLOR_FRAMES = "#2d2d2d"           # Fondo de frames y paneles
COLOR_TEXTO = "#ffffff"            # Color del texto general
COLOR_TEXTO_TITULO = "#4CAF50"     # Color del título
COLOR_TEXTO_ESTADO = "#81C784"     # Color del estado

# --- Colores de resultados ---
COLOR_ARCHIVO = "#66BB6A"          # Color para archivos
COLOR_CARPETA = "#FFA726"          # Color para carpetas
COLOR_RESULTADO_FONDO = "#333333"  # Fondo de cada resultado
COLOR_RESULTADO_BORDE = "#555555"  # Borde de cada resultado

# --- Colores de botones ---
COLOR_BOTON_BG = "#4CAF50"         # Fondo de botones
COLOR_BOTON_FG = "#ffffff"         # Texto de botones
COLOR_BOTON_DISABLED = "#666666"   # Botones deshabilitados

# --- Colores de campos de entrada ---
COLOR_ENTRY_BG = "#3c3c3c"         # Fondo de campos de texto
COLOR_ENTRY_FG = "#ffffff"         # Texto en campos de entrada
COLOR_ENTRY_SELECT = "#4CAF50"     # Selección en campos

# --- Colores de scrollbar ---
COLOR_SCROLLBAR = "#4CAF50"        # Color de la scrollbar

# ============ FUNCIONES DEL BUSCADOR ============

def buscar_completo(directorio, patron, tipo="ambos", max_resultados=None):
    """Buscador completo con opciones"""
    resultados = {
        'archivos': [],
        'carpetas': [],
        'total': 0
    }
    
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
    tiempo = fin - inicio
    
    return resultados, tiempo

def buscar_por_extension(directorio, extension):
    """Busca archivos con una extensión específica"""
    resultados = []
    
    if not extension.startswith('.'):
        extension = '.' + extension
    
    for root, dirs, files in os.walk(directorio):
        for archivo in files:
            if archivo.lower().endswith(extension.lower()):
                ruta_completa = os.path.join(root, archivo)
                resultados.append(ruta_completa)
    
    return resultados

def buscar_con_comodines(directorio, patron, tipo="ambos"):
    """Busca usando comodines"""
    resultados = []
    
    for root, dirs, files in os.walk(directorio):
        if tipo in ["archivos", "ambos"]:
            for archivo in files:
                if fnmatch.fnmatch(archivo.lower(), patron.lower()):
                    ruta = os.path.join(root, archivo)
                    resultados.append(ruta)
        
        if tipo in ["carpetas", "ambos"]:
            for carpeta in dirs:
                if fnmatch.fnmatch(carpeta.lower(), patron.lower()):
                    ruta = os.path.join(root, carpeta)
                    resultados.append(ruta)
    
    return resultados

def buscar_carpetas_por_nombre(directorio, patron):
    """Busca carpetas que contengan el patrón en el nombre"""
    resultados = []
    
    for root, dirs, files in os.walk(directorio):
        for carpeta in dirs:
            if patron.lower() in carpeta.lower():
                ruta_completa = os.path.join(root, carpeta)
                resultados.append(ruta_completa)
    
    return resultados

def buscar_archivos_por_nombre(directorio, patron, max_resultados=None):
    """Busca archivos que contengan el patrón en el nombre"""
    resultados = []
    contador = 0
    
    for root, dirs, files in os.walk(directorio):
        if max_resultados and contador >= max_resultados:
            break
            
        for archivo in files:
            if patron.lower() in archivo.lower():
                ruta_completa = os.path.join(root, archivo)
                resultados.append(ruta_completa)
                contador += 1
                
                if max_resultados and contador >= max_resultados:
                    break
    
    return resultados

# ============ FUNCIONES PARA ABRIR ARCHIVOS ============

def abrir_archivo(ruta):
    """Abre un archivo o carpeta con el programa predeterminado"""
    if not os.path.exists(ruta):
        messagebox.showerror("Error", f"La ruta no existe:\n{ruta}")
        return
    
    try:
        if platform.system() == 'Windows':
            os.startfile(ruta) #type: ignore
        elif platform.system() == 'Darwin':
            subprocess.run(['open', ruta])
        else:
            subprocess.run(['xdg-open', ruta], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir:\n{str(e)}")

def abrir_carpeta_contenedora(ruta):
    """Abre la carpeta contenedora del archivo"""
    if not os.path.exists(ruta):
        messagebox.showerror("Error", f"La ruta no existe:\n{ruta}")
        return
    
    try:
        if os.path.isfile(ruta):
            carpeta = os.path.dirname(ruta)
        else:
            carpeta = ruta
        
        abrir_archivo(carpeta)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")

def copiar_ruta_al_portapapeles(ruta):
    """Copia la ruta al portapapeles"""
    global ventana
    try:
        ventana.clipboard_clear() #type: ignore
        ventana.clipboard_append(ruta) #type: ignore
        messagebox.showinfo("Éxito", f"Ruta copiada al portapapeles:\n{ruta}")
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
resultados_actuales = []

# ============ FUNCIONES DE TKINTER ============

def centrar_ventana():
    """Centra la ventana en la pantalla"""
    global ventana
    ventana.update_idletasks() #type: ignore
    width = ventana.winfo_width() #type: ignore
    height = ventana.winfo_height() #type: ignore
    x = (ventana.winfo_screenwidth() // 2) - (width // 2) #type: ignore
    y = (ventana.winfo_screenheight() // 2) - (height // 2) #type: ignore
    ventana.geometry(f'{width}x{height}+{x}+{y}') #type: ignore

def formatear_tamaño(bytes):
    """Formatea el tamaño de bytes a una unidad legible"""
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unidad}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

def on_frame_configure(event):
    """Actualiza el área del scroll cuando cambia el frame"""
    global canvas_resultados
    canvas_resultados.configure(scrollregion=canvas_resultados.bbox('all')) #type: ignore

def on_canvas_configure(event):
    """Ajusta el ancho del frame cuando cambia el canvas"""
    global canvas_resultados
    canvas_resultados.itemconfig(1, width=event.width - 10) #type: ignore

def seleccionar_directorio():
    """Abre diálogo para seleccionar directorio"""
    global dir_busqueda, entry_dir
    directorio = filedialog.askdirectory(title="Seleccionar directorio de búsqueda")
    if directorio:
        dir_busqueda.set(directorio) #type: ignore
        entry_dir.delete(0, tk.END) #type: ignore
        entry_dir.insert(0, directorio) #type: ignore

def limpiar_resultados():
    """Limpia todos los resultados mostrados"""
    global frame_resultados, label_info, resultados_actuales
    for widget in frame_resultados.winfo_children(): #type: ignore
        widget.destroy()
    resultados_actuales = []
    label_info.config(text="") #type: ignore

def mostrar_resultado(ruta, es_archivo):
    """Muestra un resultado con sus botones"""
    global frame_resultados
    
    # Obtener solo el nombre del archivo/carpeta
    nombre = os.path.basename(ruta)
    
    # Frame para cada resultado con colores personalizados
    item_frame = tk.Frame(frame_resultados, 
                        bg=COLOR_RESULTADO_FONDO,
                        relief=tk.RAISED, 
                        borderwidth=1,
                        highlightbackground=COLOR_RESULTADO_BORDE,
                        highlightthickness=1)
    item_frame.pack(fill=tk.X, pady=2, padx=5)
    
    # Color según tipo
    if es_archivo:
        color = COLOR_ARCHIVO
        icono = "📄"
    else:
        color = COLOR_CARPETA
        icono = "📁"
    
    # Mostrar SOLO el nombre del archivo/carpeta (no la ruta completa)
    label_texto = tk.Label(item_frame, 
                        text=f"{icono} {nombre}",  # <-- SOLO EL NOMBRE
                        fg=color,
                        bg=COLOR_RESULTADO_FONDO,
                        font=('Consolas', 12, 'bold'),
                        anchor='w')
    label_texto.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
    
    # Agregar tooltip con la ruta completa al pasar el mouse
    def mostrar_ruta_completa(event):
        tooltip = tk.Toplevel(item_frame)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label_tooltip = tk.Label(tooltip, 
                            text=ruta, 
                            bg="#333333", 
                            fg="#ffffff",
                            font=('Arial', 9),
                            relief=tk.SOLID,
                            borderwidth=1,
                            padx=5,
                            pady=3)
        label_tooltip.pack()
        
        def ocultar_tooltip(event):
            tooltip.destroy()
        
        tooltip.bind('<Leave>', ocultar_tooltip)
        item_frame.tooltip = tooltip #type: ignore
    
    def ocultar_tooltip(event):
        if hasattr(item_frame, 'tooltip'):
            item_frame.tooltip.destroy() #type: ignore
    
    label_texto.bind('<Enter>', mostrar_ruta_completa)
    label_texto.bind('<Leave>', ocultar_tooltip)
    
    # Frame para botones
    btn_container = tk.Frame(item_frame, bg=COLOR_RESULTADO_FONDO)
    btn_container.pack(side=tk.RIGHT, padx=5, pady=2)
    
    # Botón Abrir
    btn_abrir = tk.Button(btn_container, 
                        text="🚀 Abrir", 
                        command=lambda: abrir_archivo(ruta),
                        bg=COLOR_BOTON_BG,
                        fg=COLOR_BOTON_FG,
                        relief=tk.FLAT,
                        padx=10,
                        pady=4,
                        cursor='hand2',
                        font=('Arial', 9))
    btn_abrir.pack(side=tk.LEFT, padx=2)
    
    # Botón Carpeta
    btn_carpeta = tk.Button(btn_container, 
                        text="📂 Carpeta", 
                        command=lambda: abrir_carpeta_contenedora(ruta),
                        bg=COLOR_BOTON_BG,
                        fg=COLOR_BOTON_FG,
                        relief=tk.FLAT,
                        padx=10,
                        pady=4,
                        cursor='hand2',
                        font=('Arial', 9))
    btn_carpeta.pack(side=tk.LEFT, padx=2)
    
    # Botón Copiar
    btn_copiar = tk.Button(btn_container, 
                        text="📋 Copiar", 
                        command=lambda: copiar_ruta_al_portapapeles(ruta),
                        bg=COLOR_BOTON_BG,
                        fg=COLOR_BOTON_FG,
                        relief=tk.FLAT,
                        padx=10,
                        pady=4,
                        cursor='hand2',
                        font=('Arial', 9))
    btn_copiar.pack(side=tk.LEFT, padx=2)
    
    # Botón Información
    btn_info = tk.Button(btn_container, 
                        text="ℹ️ Info", 
                        command=lambda: mostrar_info(ruta),
                        bg=COLOR_BOTON_BG,
                        fg=COLOR_BOTON_FG,
                        relief=tk.FLAT,
                        padx=10,
                        pady=4,
                        cursor='hand2',
                        font=('Arial', 9))
    btn_info.pack(side=tk.LEFT, padx=2)

def mostrar_info(ruta):
    """Muestra información del archivo o carpeta"""
    if not os.path.exists(ruta):
        messagebox.showerror("Error", "La ruta ya no existe")
        return
    
    nombre = os.path.basename(ruta)
    info = f"📂 Nombre: {nombre}\n"
    info += f"📌 Ruta completa: {ruta}\n\n"
    
    if os.path.isfile(ruta):
        info += f"📄 Tipo: Archivo\n"
        info += f"📏 Tamaño: {formatear_tamaño(os.path.getsize(ruta))}\n"
        info += f"📅 Modificado: {time.ctime(os.path.getmtime(ruta))}\n"
        info += f"📁 Extensión: {os.path.splitext(ruta)[1] or 'Sin extensión'}\n"
    else:
        info += f"📁 Tipo: Carpeta\n"
        info += f"📅 Modificado: {time.ctime(os.path.getmtime(ruta))}\n"
        try:
            items = os.listdir(ruta)
            info += f"📊 Contenido: {len(items)} elementos\n"
        except:
            info += "📊 Contenido: No accesible\n"
    
    messagebox.showinfo(f"Información: {nombre}", info)

def iniciar_busqueda():
    """Inicia el proceso de búsqueda"""
    global busqueda_activa, entry_busqueda, label_estado, label_info
    global btn_buscar, btn_detener, dir_busqueda, tipo_busqueda, max_resultados_var
    
    if busqueda_activa:
        return
    
    texto_buscar = entry_busqueda.get().strip() #type: ignore
    if not texto_buscar:
        messagebox.showwarning("Advertencia", "Por favor, ingresa un término de búsqueda")
        return
    
    directorio = dir_busqueda.get().strip() #type: ignore
    if not os.path.exists(directorio):
        messagebox.showerror("Error", f"El directorio no existe:\n{directorio}")
        return
    
    limpiar_resultados()
    
    label_estado.config(text="⏳ Buscando...") #type: ignore
    label_info.config(text="") #type: ignore
    btn_buscar.config(state=tk.DISABLED) #type: ignore
    btn_detener.config(state=tk.NORMAL) #type: ignore
    
    tipo = tipo_busqueda.get() #type: ignore
    max_res = max_resultados_var.get().strip() #type: ignore
    max_res = int(max_res) if max_res else None
    
    busqueda_activa = True
    
    hilo = Thread(target=ejecutar_busqueda, 
                args=(directorio, texto_buscar, tipo, max_res))
    hilo.daemon = True
    hilo.start()

def ejecutar_busqueda(directorio, patron, tipo, max_resultados):
    """Ejecuta la búsqueda en un hilo separado"""
    global ventana
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
                resultados_completos, tiempo = buscar_completo(directorio, patron, tipo, max_resultados)
                resultados = resultados_completos['archivos'] + resultados_completos['carpetas']
        
        if max_resultados and len(resultados) > max_resultados:
            resultados = resultados[:max_resultados]
        
        ventana.after(0, mostrar_resultados_en_gui, resultados, tiempo, patron) #type: ignore
        
    except Exception as e:
        ventana.after(0, mostrar_error, str(e)) #type: ignore

def mostrar_resultados_en_gui(resultados, tiempo, patron):
    """Muestra los resultados en la interfaz"""
    global busqueda_activa, btn_buscar, btn_detener, label_estado, label_info
    
    busqueda_activa = False
    btn_buscar.config(state=tk.NORMAL) #type: ignore
    btn_detener.config(state=tk.DISABLED) #type: ignore
    
    if not resultados:
        label_estado.config(text="❌ No se encontraron resultados") #type: ignore
        label_info.config(text="") #type: ignore
        messagebox.showinfo("Búsqueda completada", 
                        f"No se encontraron resultados para: '{patron}'")
        return
    
    archivos = []
    carpetas = []
    for ruta in resultados:
        if os.path.exists(ruta):
            if os.path.isfile(ruta):
                archivos.append(ruta)
            else:
                carpetas.append(ruta)
    
    for ruta in resultados:
        if os.path.exists(ruta):
            es_archivo = os.path.isfile(ruta)
            mostrar_resultado(ruta, es_archivo)
    
    label_estado.config(text=f"✅ Búsqueda completada en {tiempo:.2f} segundos") #type: ignore
    label_info.config(text=f"📊 Total: {len(resultados)} resultados " #type: ignore
                        f"(📄 {len(archivos)} archivos, 📁 {len(carpetas)} carpetas)")
    
    on_frame_configure(None)

def mostrar_error(mensaje):
    """Muestra un error en la interfaz"""
    global busqueda_activa, btn_buscar, btn_detener, label_estado
    busqueda_activa = False
    btn_buscar.config(state=tk.NORMAL) #type: ignore
    btn_detener.config(state=tk.DISABLED) #type: ignore
    label_estado.config(text="❌ Error en la búsqueda") #type: ignore
    messagebox.showerror("Error", f"Error durante la búsqueda:\n{mensaje}")

def detener_busqueda():
    """Detiene la búsqueda en curso"""
    global busqueda_activa, label_estado, btn_buscar, btn_detener
    if busqueda_activa:
        busqueda_activa = False
        label_estado.config(text="⏹ Búsqueda detenida") #type: ignore
        btn_buscar.config(state=tk.NORMAL) #type: ignore
        btn_detener.config(state=tk.DISABLED) #type: ignore

# ============ CREACIÓN DE INTERFAZ ============

def crear_interfaz():
    """Crea la interfaz gráfica completa"""
    global ventana, entry_busqueda, entry_dir, entry_max, tipo_busqueda
    global dir_busqueda, max_resultados_var, label_estado, label_info
    global btn_buscar, btn_detener, frame_resultados, canvas_resultados
    
    # Crear ventana principal con color personalizado
    ventana = tk.Tk()
    ventana.title("🔍 Buscador de Archivos - GUI")
    ventana.geometry("900x700")
    ventana.resizable(True, True)
    ventana.configure(bg=COLOR_VENTANA)
    
    # Icono de la ventana
    try:
        icono1 = Image.open("./img/icono1.png")
        icono_ventana = ImageTk.PhotoImage(icono1)
        ventana.iconphoto(False, icono_ventana) #type: ignore
    except:
        pass  # Si no hay icono, continuar sin él
    
    # Frame principal con color personalizado
    main_frame = tk.Frame(ventana, bg=COLOR_VENTANA, padx=10, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # ========== FILA 0: Título ==========
    titulo = tk.Label(main_frame, 
                    text="🔍 BUSCADOR DE ARCHIVOS", 
                    font=('Arial', 18, 'bold'),
                    fg=COLOR_TEXTO_TITULO,
                    bg=COLOR_VENTANA)
    titulo.pack(pady=10)
    
    # ========== FILA 1: Búsqueda ==========
    frame_busqueda = tk.Frame(main_frame, bg=COLOR_VENTANA)
    frame_busqueda.pack(fill=tk.X, pady=5)
    
    lbl_buscar = tk.Label(frame_busqueda, 
                        text="Buscar:", 
                        font=('Arial', 14),
                        fg=COLOR_TEXTO,
                        bg=COLOR_VENTANA)
    lbl_buscar.pack(side=tk.LEFT, padx=5)
    
    entry_busqueda = tk.Entry(frame_busqueda, 
                            font=('Arial', 14),
                            bg=COLOR_ENTRY_BG,
                            fg=COLOR_ENTRY_FG,
                            selectbackground=COLOR_ENTRY_SELECT,
                            insertbackground=COLOR_TEXTO,
                            relief=tk.FLAT,
                            width=50)
    entry_busqueda.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    entry_busqueda.bind('<Return>', lambda e: iniciar_busqueda())
    
    # Botones de acción
    btn_frame = tk.Frame(frame_busqueda, bg=COLOR_VENTANA)
    btn_frame.pack(side=tk.RIGHT, padx=5)
    
    btn_buscar = tk.Button(btn_frame, 
                        text="🔍 Buscar", 
                        command=iniciar_busqueda,
                        bg=COLOR_BOTON_BG,
                        fg=COLOR_BOTON_FG,
                        relief=tk.FLAT,
                        padx=15,
                        pady=5,
                        cursor='hand2',
                        font=('Arial', 10, 'bold'))
    btn_buscar.pack(side=tk.LEFT, padx=2)
    
    btn_detener = tk.Button(btn_frame, 
                        text="⏹ Detener", 
                        command=detener_busqueda,
                        state=tk.DISABLED,
                        bg=COLOR_BOTON_DISABLED,
                        fg=COLOR_BOTON_FG,
                        relief=tk.FLAT,
                        padx=15,
                        pady=5,
                        cursor='hand2',
                        font=('Arial', 10, 'bold'))
    btn_detener.pack(side=tk.LEFT, padx=2)
    
    # ========== FILA 2: Opciones ==========
    options_frame = tk.LabelFrame(main_frame, 
                                text="Opciones de Búsqueda",
                                fg=COLOR_TEXTO,
                                bg=COLOR_FRAMES,
                                font=('Arial', 12),
                                padx=10,
                                pady=10)
    options_frame.pack(fill=tk.X, pady=10)
    
    # Tipo de búsqueda
    frame_tipo = tk.Frame(options_frame, bg=COLOR_FRAMES)
    frame_tipo.pack(anchor=tk.W, pady=5)
    
    lbl_tipo = tk.Label(frame_tipo, 
                    text="Tipo:", 
                    fg=COLOR_TEXTO,
                    bg=COLOR_FRAMES,
                    font=('Arial', 11))
    lbl_tipo.pack(side=tk.LEFT, padx=5)
    
    tipo_busqueda = tk.StringVar(value="ambos")
    
    # Crear radiobuttons personalizados
    def crear_radiobutton(parent, text, value, var):
        rb = tk.Radiobutton(parent, 
                        text=text, 
                        variable=var, 
                        value=value,
                        fg=COLOR_TEXTO,
                        bg=COLOR_FRAMES,
                        selectcolor=COLOR_FRAMES,
                        activebackground=COLOR_FRAMES,
                        font=('Arial', 11))
        return rb
    
    rb_ambos = crear_radiobutton(frame_tipo, "Archivos y carpetas", "ambos", tipo_busqueda)
    rb_ambos.pack(side=tk.LEFT, padx=10)
    
    rb_archivos = crear_radiobutton(frame_tipo, "Solo archivos", "archivos", tipo_busqueda)
    rb_archivos.pack(side=tk.LEFT, padx=10)
    
    rb_carpetas = crear_radiobutton(frame_tipo, "Solo carpetas", "carpetas", tipo_busqueda)
    rb_carpetas.pack(side=tk.LEFT, padx=10)
    
    # Directorio de búsqueda
    frame_dir = tk.Frame(options_frame, bg=COLOR_FRAMES)
    frame_dir.pack(fill=tk.X, pady=5)
    
    lbl_dir = tk.Label(frame_dir, 
                    text="Directorio:", 
                    fg=COLOR_TEXTO,
                    bg=COLOR_FRAMES,
                    font=('Arial', 11))
    lbl_dir.pack(side=tk.LEFT, padx=5)
    
    dir_busqueda = tk.StringVar(value=os.path.expanduser("~"))
    entry_dir = tk.Entry(frame_dir, 
                        textvariable=dir_busqueda,
                        bg=COLOR_ENTRY_BG,
                        fg=COLOR_ENTRY_FG,
                        selectbackground=COLOR_ENTRY_SELECT,
                        insertbackground=COLOR_TEXTO,
                        relief=tk.FLAT,
                        width=50,
                        font=('Arial', 11))
    entry_dir.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    btn_examinar = tk.Button(frame_dir, 
                            text="📁 Examinar", 
                            command=seleccionar_directorio,
                            bg=COLOR_BOTON_BG,
                            fg=COLOR_BOTON_FG,
                            relief=tk.FLAT,
                            padx=10,
                            pady=2,
                            cursor='hand2',
                            font=('Arial', 10))
    btn_examinar.pack(side=tk.RIGHT, padx=5)
    
    # Límite de resultados
    frame_max = tk.Frame(options_frame, bg=COLOR_FRAMES)
    frame_max.pack(fill=tk.X, pady=5)
    
    lbl_max = tk.Label(frame_max, 
                    text="Máx resultados:", 
                    fg=COLOR_TEXTO,
                    bg=COLOR_FRAMES,
                    font=('Arial', 11))
    lbl_max.pack(side=tk.LEFT, padx=5)
    
    max_resultados_var = tk.StringVar(value="")
    entry_max = tk.Entry(frame_max, 
                        textvariable=max_resultados_var,
                        bg=COLOR_ENTRY_BG,
                        fg=COLOR_ENTRY_FG,
                        selectbackground=COLOR_ENTRY_SELECT,
                        insertbackground=COLOR_TEXTO,
                        relief=tk.FLAT,
                        width=10,
                        font=('Arial', 11))
    entry_max.pack(side=tk.LEFT, padx=5)
    
    lbl_limite = tk.Label(frame_max, 
                        text="(dejar vacío = sin límite)", 
                        fg=COLOR_TEXTO,
                        bg=COLOR_FRAMES,
                        font=('Arial', 10))
    lbl_limite.pack(side=tk.LEFT, padx=10)
    
    # ========== FILA 3: Estado ==========
    label_estado = tk.Label(main_frame, 
                        text="✅ Listo", 
                        font=('Arial', 12),
                        fg=COLOR_TEXTO_ESTADO,
                        bg=COLOR_VENTANA)
    label_estado.pack(anchor=tk.W, pady=5)
    
    # ========== FILA 4: Resultados ==========
    results_frame = tk.LabelFrame(main_frame, 
                                text="Resultados",
                                fg=COLOR_TEXTO,
                                bg=COLOR_FRAMES,
                                font=('Arial', 12),
                                padx=5,
                                pady=5)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Canvas para scroll de resultados
    canvas_resultados = tk.Canvas(results_frame, 
                                bg=COLOR_VENTANA,
                                highlightthickness=0)
    canvas_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Scrollbar con color personalizado
    scrollbar = tk.Scrollbar(results_frame, 
                            orient=tk.VERTICAL,
                            command=canvas_resultados.yview,
                            bg=COLOR_SCROLLBAR,
                            troughcolor=COLOR_FRAMES,
                            activebackground=COLOR_SCROLLBAR)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas_resultados.configure(yscrollcommand=scrollbar.set)
    
    # Frame contenedor para los resultados
    frame_resultados = tk.Frame(canvas_resultados, bg=COLOR_VENTANA)
    canvas_resultados.create_window((0, 0), window=frame_resultados, 
                                anchor='nw', width=850)
    
    # Actualizar scroll cuando cambia el tamaño
    frame_resultados.bind('<Configure>', on_frame_configure)
    canvas_resultados.bind('<Configure>', on_canvas_configure)
    
    # ========== FILA 5: Información ==========
    label_info = tk.Label(main_frame, 
                        text="", 
                        font=('Arial', 12),
                        fg=COLOR_TEXTO,
                        bg=COLOR_VENTANA)
    label_info.pack(anchor=tk.W, pady=5)
    
    # Atajos de teclado
    ventana.bind('<Control-f>', lambda e: entry_busqueda.focus()) #type: ignore
    ventana.bind('<Control-F>', lambda e: entry_busqueda.focus()) #type: ignore
    
    # Centrar ventana
    centrar_ventana()
    
    return ventana

# ============ FUNCIÓN PRINCIPAL ============

def main():
    global ventana
    ventana = crear_interfaz()
    ventana.mainloop()

if __name__ == '__main__':
    main()