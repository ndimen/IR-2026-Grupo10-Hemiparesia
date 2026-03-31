import customtkinter as ctk

# --- CONSTANTES VISUALES PARA EL MENÚ ---
COLOR_PANEL_2 = "#334155"
COLOR_TEXTO = "#F8FAFC"
COLOR_SUBTEXTO = "#CBD5E1"
COLOR_ERROR = "#EF4444"
FUENTE_TITULO = ("Arial", 28, "bold")

def crear_pantalla_login(app):
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
        frame, "Ingresar", lambda: procesar_login(app), width=340
    ).pack(pady=10)

def procesar_login(app):
    nombre = app.entry_nombre.get().strip()
    dni = app.entry_dni_login.get().strip()

    # 1. Validar nombre
    if not nombre:
        app.label_error_login.configure(text="Por favor, ingresá el nombre.")
        return

    # 2. Validar que el DNI no esté vacío
    if not dni:
        app.label_error_login.configure(text="Por favor, ingresá el DNI.")
        return
        
    # 3. Validar que SOLO tenga números (Rechaza letras, espacios o símbolos)
    if not dni.isdigit():
        app.label_error_login.configure(text="Error: el DNI debe contener solo números.")
        return

    # 4. Lógica de auto-corrección de 7 a 8 dígitos
    if len(dni) == 7:
        dni = "0" + dni  # Agrega el cero al principio automáticamente
    elif len(dni) != 8:
        # Si tiene 5, 6, o 9 números, no lo deja pasar
        app.label_error_login.configure(text="Error: el DNI debe tener 7 u 8 números.")
        return

    # Si todo está correcto, borramos cualquier mensaje de error anterior
    app.label_error_login.configure(text="")
    
    # Guardamos los datos en la app principal y avanzamos al menú
    app.nombre_paciente = nombre
    app.id_paciente = dni
    crear_pantalla_menu(app)
    
def crear_pantalla_menu(app):
    app.limpiar_ventana()

    frame = app.crear_tarjeta_centrada(relwidth=0.60, relheight=0.75)

    ctk.CTkLabel(
        frame,
        text=f"Paciente: {app.nombre_paciente} | DNI: {app.id_paciente}",
        font=("Arial", 18, "bold"), text_color=COLOR_SUBTEXTO
    ).pack(pady=(30, 5))

    ctk.CTkLabel(
        frame, text="Seleccioná un juego", font=FUENTE_TITULO, text_color=COLOR_TEXTO
    ).pack(pady=(0, 40))

    # Botón que lleva a Fitts
    app.crear_boton_principal(
        frame, "Juego 1: Ley de Fitts", app.crear_pantalla_inicio, width=320
    ).pack(pady=15)

    app.crear_boton_principal(
        frame, "Juego 2: Próximamente", lambda: print("Cargar juego 2..."),
        color=COLOR_PANEL_2, hover="#1E293B", width=320
    ).pack(pady=15)

    app.crear_boton_principal(
        frame, "Juego 3: Próximamente", lambda: print("Cargar juego 3..."),
        color=COLOR_PANEL_2, hover="#1E293B", width=320
    ).pack(pady=15)

    app.crear_boton_principal(
        frame, "Cerrar Sesión", lambda: crear_pantalla_login(app),
        color=COLOR_ERROR, hover="#B91C1C", width=200
    ).pack(pady=(30, 0))