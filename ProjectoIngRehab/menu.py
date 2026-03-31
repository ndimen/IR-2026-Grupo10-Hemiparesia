import customtkinter as ctk

# --- CONSTANTES VISUALES ---
COLOR_PANEL_2 = "#334155"
COLOR_TEXTO = "#F8FAFC"
COLOR_SUBTEXTO = "#CBD5E1"
COLOR_ERROR = "#EF4444"
FUENTE_TITULO = ("Arial", 28, "bold")

def crear_pantalla_login(app):
    """Interfaz de inicio de sesión"""
    app.limpiar_ventana()
    
    frame = app.crear_tarjeta_centrada(relwidth=0.55, relheight=0.65)

    ctk.CTkLabel(
        frame, text="Iniciar Sesión", font=FUENTE_TITULO, text_color=COLOR_TEXTO
    ).pack(pady=(40, 30))

    app.entry_nombre = ctk.CTkEntry(
        frame, placeholder_text="Nombre del paciente",
        width=340, height=52, corner_radius=14, font=("Arial", 18),
        fg_color="#0B1220", border_color=COLOR_PANEL_2, text_color=COLOR_TEXTO
    )
    app.entry_nombre.pack(pady=(0, 20))

    app.entry_dni_login = ctk.CTkEntry(
        frame, placeholder_text="DNI del paciente",
        width=340, height=52, corner_radius=14, font=("Arial", 18),
        fg_color="#0B1220", border_color=COLOR_PANEL_2, text_color=COLOR_TEXTO
    )
    app.entry_dni_login.pack(pady=(0, 20))

    app.label_error_login = ctk.CTkLabel(
        frame, text="", font=("Arial", 16, "bold"), text_color=COLOR_ERROR
    )
    app.label_error_login.pack(pady=(0, 10))

    app.crear_boton_principal(
        frame, "Ingresar al Sistema", lambda: procesar_login(app), width=340
    ).pack(pady=10)

def procesar_login(app):
    """Valida datos y pasa al menú"""
    nombre = app.entry_nombre.get().strip()
    dni = app.entry_dni_login.get().strip()

    if not nombre or not dni:
        app.label_error_login.configure(text="Por favor, completa todos los campos.")
        return
        
    if not dni.isdigit():
        app.label_error_login.configure(text="El DNI debe contener solo números.")
        return

    app.nombre_paciente = nombre
    app.id_paciente = dni
    
    crear_pantalla_menu(app)
    
def crear_pantalla_menu(app):
    """Selector de juegos principal"""
    app.limpiar_ventana()

    frame = ctk.CTkFrame(app, fg_color="#1E293B", corner_radius=20)
    frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.60, relheight=0.8)

    ctk.CTkLabel(
        frame,
        text=f"Paciente: {app.nombre_paciente} | DNI: {app.id_paciente}",
        font=("Arial", 16, "bold"), text_color=COLOR_SUBTEXTO
    ).pack(pady=(30, 5))

    ctk.CTkLabel(
        frame, text="Panel de Rehabilitación", font=FUENTE_TITULO, text_color=COLOR_TEXTO
    ).pack(pady=(0, 40))

    # --- BLOQUE DE IMPORTACIÓN Y DEBUG ---
    try:
        from ingenrehab2 import FittsApp
        print("Juego 1 cargado OK")
        from DragNDrop import DragDropGame
        print("Juego 2 cargado OK")
        from test3 import MazeApp
        print("Juego 3 cargado OK")
    except ImportError as e:
        print(f"ERROR CRÍTICO DE IMPORTACIÓN: {e}")
        FittsApp = DragDropGame = MazeApp = None

    def crear_btn_lanzador(texto, clase_juego, color):
        """Crea el botón que activa el juego en el main.py"""
        estado = "normal" if clase_juego else "disabled"
        
        ctk.CTkButton(
            frame, text=texto, 
            command=lambda: app.lanzar_juego(clase_juego),
            width=380, height=60, corner_radius=12,
            font=("Arial", 18, "bold"), fg_color=color, state=estado
        ).pack(pady=12)

    # Configuración de los 3 botones
    crear_btn_lanzador("Juego 1: Ley de Fitts (Puntería)", FittsApp, "#38BDF8")
    crear_btn_lanzador("Juego 2: Arrastre (Drag & Drop)", DragDropGame, "#818CF8")
    crear_btn_lanzador("Juego 3: Test de Control (Laberinto)", MazeApp, "#F472B6")

    # Botón Salir
    ctk.CTkButton(
        frame, text="Cerrar Sesión", 
        command=lambda: crear_pantalla_login(app),
        fg_color=COLOR_ERROR, hover_color="#B91C1C", 
        width=200, height=40, corner_radius=10
    ).pack(pady=(40, 0))