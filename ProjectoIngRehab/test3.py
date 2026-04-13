import customtkinter as ctk
import tkinter as tk
import json
import os
import time
import math
import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
import platform
import subprocess
import menu

# ----------------------------
# CONFIGURACIÓN VISUAL
# ----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ANCHO = 1100
ALTO = 760

COLOR_FONDO    = "#0F172A"
COLOR_PANEL    = "#1E293B"
COLOR_PANEL_2  = "#334155"
COLOR_TEXTO    = "#F8FAFC"
COLOR_SUBTEXTO = "#CBD5E1"
COLOR_ACCION   = "#22C55E"
COLOR_ACCION_HOVER = "#16A34A"
COLOR_ALERTA   = "#F59E0B"
COLOR_ERROR    = "#EF4444"
COLOR_OBJETIVO = "#F97316"

FUENTE_TITULO       = ("Arial", 30, "bold")
FUENTE_TEXTO        = ("Arial", 18)
FUENTE_TEXTO_GRANDE = ("Arial", 22, "bold")
FUENTE_BOTON        = ("Arial", 18, "bold")

# Configuracion del corredor
GROSOR_CAMINO = 36   # radio del tubo (px)
GROSOR_PARED  = 7    # grosor del borde visual

# Rango de cantidad de laberintos configurables
MIN_LABERINTOS     = 1
MAX_LABERINTOS     = 10
DEFAULT_LABERINTOS = 3

# Dimensiones del canvas de juego
CANVAS_ALTO = ALTO - 120
MARGEN      = 80

# ----------------------------
# GENERADOR ALEATORIO
# ----------------------------

def generar_laberinto_aleatorio(dificultad=1):
    """
    Genera waypoints para un corredor aleatorio horizontal.
    dificultad 1=facil / 2=medio / 3=dificil.
    Garantiza que el camino va de izquierda a derecha y cabe en el canvas.
    """
    if dificultad == 1:
        num_seg   = random.randint(4, 6)
        paso_min, paso_max = 150, 230
    elif dificultad == 2:
        num_seg   = random.randint(6, 9)
        paso_min, paso_max = 110, 180
    else:
        num_seg   = random.randint(9, 13)
        paso_min, paso_max = 80, 150

    for _ in range(50):   # reintentos
        x = MARGEN
        y = random.randint(CANVAS_ALTO // 4, 3 * CANVAS_ALTO // 4)
        wps = [(x, y)]
        dir_horizontal = True   # alternamos H/V empezando en H
        ok = True

        for i in range(num_seg):
            es_ultimo = (i == num_seg - 1)
            paso = random.randint(paso_min, paso_max)

            if es_ultimo or dir_horizontal:
                # Movimiento horizontal hacia la derecha
                nx = x + paso
                ny = y
                dir_horizontal = False
            else:
                # Movimiento vertical
                signo = random.choice([-1, 1])
                ny_prop = y + signo * paso
                if ny_prop < MARGEN or ny_prop > CANVAS_ALTO - MARGEN:
                    signo *= -1
                    ny_prop = y + signo * paso
                ny_prop = max(MARGEN, min(CANVAS_ALTO - MARGEN, ny_prop))
                nx, ny = x, ny_prop
                dir_horizontal = True

            if nx > ANCHO - MARGEN:
                nx = ANCHO - MARGEN
                wps.append((nx, ny))
                break

            if ny < MARGEN or ny > CANVAS_ALTO - MARGEN:
                ok = False
                break

            wps.append((nx, ny))
            x, y = nx, ny

        if not ok or len(wps) < 3:
            continue
        if wps[-1][0] < ANCHO * 0.60:
            continue

        return wps

    # Fallback garantizado: forma de S simple
    mid = CANVAS_ALTO // 2
    return [
        (MARGEN,       mid),
        (270,          mid),
        (270,          mid - 120),
        (540,          mid - 120),
        (540,          mid + 120),
        (810,          mid + 120),
        (810,          mid),
        (ANCHO - MARGEN, mid),
    ]


def interpolar_camino(waypoints, pasos=1200):
    """Puntos densos a lo largo del camino central."""
    puntos = []
    n = len(waypoints) - 1
    if n == 0:
        return list(waypoints)
    por_seg = max(1, pasos // n)
    for i in range(n):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        for t in range(por_seg):
            f = t / por_seg
            puntos.append((x1 + (x2 - x1) * f, y1 + (y2 - y1) * f))
    puntos.append(waypoints[-1])
    return puntos


def distancia_al_camino(px, py, camino_puntos):
    return min(math.hypot(px - cx, py - cy) for cx, cy in camino_puntos)


def dificultad_para_laberinto(idx, total):
    if total <= 1:
        return 1
    frac = idx / (total - 1)
    if frac < 0.34:
        return 1
    elif frac < 0.67:
        return 2
    return 3


# ----------------------------
# APP
# ----------------------------
class MazeApp(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#0F172A")
        self.parent = parent
        # Asegúrate de que COLOR_FONDO esté definido arriba en tu archivo
        self.configure(fg_color=COLOR_FONDO) 

        # 👇 1. Tomamos los datos del paciente desde el main.py
        self.id_paciente = parent.id_paciente
        self.nombre_paciente = parent.nombre_paciente
        
        
        # Variable por defecto para los laberintos
        self.num_laberintos = DEFAULT_LABERINTOS

        # --- AQUÍ MANTENEMOS TUS VARIABLES ORIGINALES ---
        self.secuencia_waypoints = []
        self.resultados_laberintos = []
        self.laberinto_actual = 0
        
        self.waypoints = []
        self.camino_puntos = []
        
        self.recorriendo = False
        self.inicio_alcanzado = False
        self.tiempo_inicio = None
        self.tiempo_fin = None
        self.colisiones = 0
        self.muestras_fuera = 0
        self.total_muestras = 0
        self.trayectoria = []
        self._colision_activa = False

        # 👇 2. Llamamos a la primera pantalla de tu juego
        self.crear_pantalla_inicio()

    # ----------------------------
    # UTILIDADES
    # ----------------------------
    def limpiar_ventana(self):
        for w in self.winfo_children():
            w.destroy()

    def validar_dni(self, dni):
        dni = dni.strip()
        if not dni:
            return False, "Por favor, ingresa el DNI."
        if not dni.isdigit():
            return False, "Error: el DNI debe contener solo numeros."
        if len(dni) not in [7, 8]:
            return False, "Error: el DNI es incorrecto."
        return True, ""

    def crear_tarjeta_centrada(self, relwidth=0.68, relheight=0.74):
        f = ctk.CTkFrame(self, corner_radius=24,
                         fg_color=COLOR_PANEL,
                         border_width=2, border_color=COLOR_PANEL_2)
        f.place(relx=0.5, rely=0.5, anchor="center",
                relwidth=relwidth, relheight=relheight)
        return f

    def crear_boton_principal(self, master, text, command,
                              color=COLOR_ACCION, hover=COLOR_ACCION_HOVER, width=260):
        return ctk.CTkButton(
            master, text=text, command=command,
            width=width, height=54, corner_radius=16,
            fg_color=color, hover_color=hover,
            text_color=COLOR_TEXTO, font=FUENTE_BOTON
        )

    def abrir_archivo(self, ruta):
        try:
            ruta = os.path.abspath(ruta)
            s = platform.system()
            if s == "Windows":   os.startfile(ruta)
            elif s == "Darwin":  subprocess.run(["open", ruta])
            else:                subprocess.run(["xdg-open", ruta])
        except Exception as e:
            print("No se pudo abrir:", e)

    # ----------------------------
    # PANTALLA INICIO
    # ----------------------------
    def crear_pantalla_inicio(self):
        self.limpiar_ventana()
        self.entry_paciente    = None
        self.label_error_inicio = None
        self._num_lab_var      = None

        frame = self.crear_tarjeta_centrada(relwidth=0.64, relheight=0.88)

        ctk.CTkLabel(frame, text="OpenRehab ACV",
                     font=("Arial", 18, "bold"),
                     text_color=COLOR_SUBTEXTO).pack(pady=(18, 6))

        ctk.CTkLabel(frame, text="Test de Estabilidad Motora",
                     font=FUENTE_TITULO,
                     text_color=COLOR_TEXTO).pack(pady=(0, 8))

        ctk.CTkLabel(frame, text="Evaluacion de ruido motor y espasticidad",
                     font=FUENTE_TEXTO,
                     text_color=COLOR_SUBTEXTO).pack(pady=(0, 20))

        # Campo DNI
        """"
        self.entry_paciente = ctk.CTkEntry(
            frame, placeholder_text="Ingresar DNI del paciente",
            width=340, height=52, corner_radius=14,
            font=("Arial", 18), fg_color="#0B1220",
            border_color=COLOR_PANEL_2, text_color=COLOR_TEXTO
        )
        self.entry_paciente.pack(pady=(0, 18))
        """

        # ── Selector de cantidad de laberintos ──
        caja = ctk.CTkFrame(frame, fg_color="#0B1220", corner_radius=16)
        caja.pack(pady=(0, 18), padx=50, fill="x")

        ctk.CTkLabel(caja, text="Cantidad de laberintos por sesion:",
                     font=("Arial", 17, "bold"),
                     text_color=COLOR_TEXTO).pack(side="left", padx=20, pady=16)

        spin = ctk.CTkFrame(caja, fg_color="transparent")
        spin.pack(side="right", padx=20, pady=10)

        self._num_lab_var = tk.IntVar(value=self.num_laberintos)

        ctk.CTkButton(spin, text="−", width=44, height=44,
                      corner_radius=10, font=("Arial", 22, "bold"),
                      fg_color=COLOR_PANEL_2, hover_color="#475569",
                      command=self._dec_labs).pack(side="left", padx=4)

        ctk.CTkLabel(spin, textvariable=self._num_lab_var,
                     font=("Arial", 24, "bold"),
                     text_color=COLOR_ALERTA, width=52).pack(side="left", padx=6)

        ctk.CTkButton(spin, text="+", width=44, height=44,
                      corner_radius=10, font=("Arial", 22, "bold"),
                      fg_color=COLOR_PANEL_2, hover_color="#475569",
                      command=self._inc_labs).pack(side="left", padx=4)

        ctk.CTkLabel(
            frame,
            text=(
                "El paciente guia el cursor por un corredor sin tocar los bordes.\n"
                "Cada laberinto se genera aleatoriamente.\n"
                "La dificultad aumenta progresivamente durante la sesion."
            ),
            font=FUENTE_TEXTO, justify="center",
            text_color=COLOR_SUBTEXTO
        ).pack(pady=(4, 14))

        self.label_error_inicio = ctk.CTkLabel(
            frame, text="", font=("Arial", 16, "bold"), text_color=COLOR_ERROR)
        self.label_error_inicio.pack(pady=(0, 6))

        self.crear_boton_principal(
            frame, "Ver instrucciones",
            self.validar_e_ir_a_instrucciones,
            color="#3B82F6", hover="#2563EB").pack(pady=8)

        self.crear_boton_principal(
            frame, "Comenzar evaluacion",
            self.crear_pantalla_listo).pack(pady=8)
        
        self.crear_boton_principal(
            frame,
            "Volver al Menú",
            lambda: menu.crear_pantalla_menu(self.parent),
            color="#64748B",
            hover="#475569"
        ).pack(pady=10)

    def _dec_labs(self):
        v = self._num_lab_var.get()
        if v > MIN_LABERINTOS:
            self._num_lab_var.set(v - 1)

    def _inc_labs(self):
        v = self._num_lab_var.get()
        if v < MAX_LABERINTOS:
            self._num_lab_var.set(v + 1)

    # ----------------------------
    # VALIDACION
    # ----------------------------
    def validar_e_ir_a_instrucciones(self):
        self.num_laberintos = self._num_lab_var.get() if self._num_lab_var else DEFAULT_LABERINTOS

        if not self.id_paciente:
            self.label_error_inicio.configure(
                text="No hay un paciente cargado. Volve al menu principal."
            )
            return

        self.label_error_inicio.configure(text="")
        self.crear_pantalla_instrucciones()
    # ----------------------------
    # INSTRUCCIONES
    # ----------------------------
    def crear_pantalla_instrucciones(self):
        self.limpiar_ventana()
        frame = self.crear_tarjeta_centrada(relwidth=0.72, relheight=0.82)

        ctk.CTkLabel(frame, text="Instrucciones",
                     font=FUENTE_TITULO, text_color=COLOR_TEXTO).pack(pady=(28, 18))

        bloque = ctk.CTkFrame(frame, fg_color="#0B1220", corner_radius=20)
        bloque.pack(padx=40, pady=10, fill="both", expand=False)

        texto = (
            "1. Aparecera un corredor con dos marcas: INICIO y FIN.\n\n"
            "2. Posiciona el cursor sobre la marca INICIO (verde).\n\n"
            "3. Guia el cursor hasta la marca FIN (naranja) sin salirte.\n\n"
            "4. Cada laberinto es diferente y generado al azar.\n\n"
            f"5. La sesion tiene {self.num_laberintos} laberinto(s). La dificultad\n"
            "   aumenta progresivamente.\n\n"
            "Importante:\n"
            "  - Cada vez que el cursor toque el borde cuenta como error.\n"
            "  - Al finalizar se genera un informe PDF con los resultados."
        )

        ctk.CTkLabel(bloque, text=texto,
                     font=("Arial", 20), justify="left",
                     text_color=COLOR_TEXTO, wraplength=650).pack(padx=28, pady=28)

        ctk.CTkLabel(frame, text="Cuando estes listo/a, presiona comenzar.",
                     font=FUENTE_TEXTO_GRANDE,
                     text_color=COLOR_ALERTA).pack(pady=(20, 18))

        self.crear_boton_principal(frame, "Comenzar",
                                   self.iniciar_test, width=280).pack(pady=10)
        self.crear_boton_principal(frame, "Volver",
                                   self.crear_pantalla_inicio,
                                   color="#64748B", hover="#475569",
                                   width=280).pack(pady=10)
    
    def crear_pantalla_listo(self):
    # GENERA LABERINTOS ACÁ
        self.num_laberintos = self._num_lab_var.get() if self._num_lab_var else DEFAULT_LABERINTOS

        self.secuencia_waypoints = [
            generar_laberinto_aleatorio(
                dificultad=dificultad_para_laberinto(i, self.num_laberintos)
            )
            for i in range(self.num_laberintos)
        ]

        self.laberinto_actual = 0
        self.resultados_laberintos = []

        # UI
        self.limpiar_ventana()

        frame = self.crear_tarjeta_centrada(relwidth=0.60, relheight=0.60)

        ctk.CTkLabel(
            frame,
            text="¿Está listo?",
            font=("Arial", 34, "bold"),
            text_color=COLOR_TEXTO
        ).pack(pady=(50, 20))

        ctk.CTkLabel(
            frame,
            text="Cuando presione el botón, comenzará la evaluación.",
            font=("Arial", 22),
            text_color=COLOR_SUBTEXTO,
            justify="center"
        ).pack(pady=(0, 30))

        ctk.CTkLabel(
            frame,
            text="Coloquese sobre el boton verde y siga el camino hasta el naranja.",
            font=("Arial", 20, "bold"),
            text_color=COLOR_ALERTA,
            justify="center"
        ).pack(pady=(0, 35))
        
        self.crear_boton_principal(
            frame,
            "Sí, comenzar",
            self.iniciar_cuenta_regresiva,
            width=280
        ).pack(pady=12)

        self.crear_boton_principal(
            frame,
            "Volver",
            self.crear_pantalla_inicio,
            color="#64748B",
            hover="#475569",
            width=280
        ).pack(pady=12)


    # ----------------------------
    # CUENTA REGRESIVA
    # ----------------------------
    def iniciar_cuenta_regresiva(self):
        self.limpiar_ventana()
        frame = self.crear_tarjeta_centrada(relwidth=0.55, relheight=0.55)
        self.countdown_label = ctk.CTkLabel(
            frame, text="3", font=("Arial", 90, "bold"), text_color=COLOR_ALERTA)
        self.countdown_label.pack(expand=True)
        self.after(1000, lambda: self._tick(2))

    def _tick(self, n):
        if n > 0:
            self.countdown_label.configure(text=str(n))
            self.after(1000, lambda: self._tick(n - 1))
        else:
            self.countdown_label.configure(text="Comienza!", text_color=COLOR_ACCION)
            self.after(800, self.comenzar_laberinto_actual)

    # ----------------------------
    # INICIO DEL TEST
    # ----------------------------
    def iniciar_test(self):
        if not self.id_paciente:
            if self.label_error_inicio is not None and self.label_error_inicio.winfo_exists():
                self.label_error_inicio.configure(
                    text="No hay un paciente cargado. Volve al menu principal."
                )
            return

        self.num_laberintos = self._num_lab_var.get() if self._num_lab_var else DEFAULT_LABERINTOS

        # Generar toda la secuencia aleatoria de una sola vez
        self.secuencia_waypoints = [
            generar_laberinto_aleatorio(
                dificultad=dificultad_para_laberinto(i, self.num_laberintos)
            )
            for i in range(self.num_laberintos)
        ]

        self.laberinto_actual = 0
        self.resultados_laberintos = []
        self.crear_pantalla_listo()

    # ----------------------------
    # LABERINTO
    # ----------------------------
    def comenzar_laberinto_actual(self):
        self.limpiar_ventana()

        self.waypoints    = self.secuencia_waypoints[self.laberinto_actual]
        self.camino_puntos = interpolar_camino(self.waypoints)

        self.recorriendo      = False
        self.inicio_alcanzado = False
        self.tiempo_inicio    = None
        self.tiempo_fin       = None
        self.colisiones       = 0
        self.muestras_fuera   = 0
        self.total_muestras   = 0
        self.trayectoria      = []
        self._colision_activa = False

        dif     = dificultad_para_laberinto(self.laberinto_actual, self.num_laberintos)
        dif_txt = {1: "Facil", 2: "Medio", 3: "Dificil"}.get(dif, "")

        # Panel superior
        top = ctk.CTkFrame(self, height=120, corner_radius=0, fg_color=COLOR_PANEL)
        top.pack(fill="x")

        info = ctk.CTkFrame(top, fg_color=COLOR_PANEL, corner_radius=0)
        info.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(info, text=f"Paciente: {self.id_paciente}",
                     font=("Arial", 20, "bold"),
                     text_color=COLOR_TEXTO).grid(row=0, column=0, padx=10, pady=6, sticky="w")

        ctk.CTkLabel(info,
                     text=f"Laberinto {self.laberinto_actual + 1} / {self.num_laberintos}  |  {dif_txt}",
                     font=("Arial", 20, "bold"),
                     text_color=COLOR_TEXTO).grid(row=0, column=1, padx=10, pady=6)

        self.label_errores = ctk.CTkLabel(info, text="Colisiones: 0",
                                          font=("Arial", 20, "bold"),
                                          text_color=COLOR_TEXTO)
        self.label_errores.grid(row=0, column=2, padx=10, pady=6, sticky="e")

        self.label_estado = ctk.CTkLabel(
            info,
            text="Posiciona el cursor sobre el punto  INICIO",
            font=("Arial", 22, "bold"), text_color=COLOR_ALERTA)
        self.label_estado.grid(row=1, column=0, columnspan=3, pady=(8, 0))

        info.grid_columnconfigure(0, weight=1)
        info.grid_columnconfigure(1, weight=1)
        info.grid_columnconfigure(2, weight=1)

        # Canvas
        self.canvas = tk.Canvas(
            self, width=ANCHO, height=CANVAS_ALTO,
            bg=COLOR_FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._dibujar_laberinto()
        self.canvas.bind("<Motion>",   self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_click)
        self.cursor_id = None

    def _dibujar_laberinto(self):
        self.canvas.delete("all")
        pts = self.waypoints
        r, g = GROSOR_CAMINO, GROSOR_PARED

        for i in range(len(pts) - 1):
            x1, y1 = pts[i]; x2, y2 = pts[i + 1]
            # Sombra
            self.canvas.create_line(x1, y1, x2, y2,
                                    width=(r + g + 8) * 2, fill="#0B1220",
                                    capstyle=tk.ROUND, joinstyle=tk.ROUND)
            # Pared (borde azul)
            self.canvas.create_line(x1, y1, x2, y2,
                                    width=(r + g) * 2, fill="#38BDF8",
                                    capstyle=tk.ROUND, joinstyle=tk.ROUND)
            # Interior del corredor
            self.canvas.create_line(x1, y1, x2, y2,
                                    width=r * 2, fill="#1E3A5F",
                                    capstyle=tk.ROUND, joinstyle=tk.ROUND)

        rm = 20
        # INICIO verde
        xi, yi = pts[0]
        self.canvas.create_oval(xi-rm-4, yi-rm-4, xi+rm+4, yi+rm+4,
                                 fill="#166534", outline="")
        self.canvas.create_oval(xi-rm, yi-rm, xi+rm, yi+rm,
                                 fill=COLOR_ACCION, outline="")
        self.canvas.create_text(xi, yi, text="IN",
                                 fill="white", font=("Arial", 11, "bold"))
        # FIN naranja
        xf, yf = pts[-1]
        self.canvas.create_oval(xf-rm-4, yf-rm-4, xf+rm+4, yf+rm+4,
                                 fill="#7C2D12", outline="")
        self.canvas.create_oval(xf-rm, yf-rm, xf+rm, yf+rm,
                                 fill=COLOR_OBJETIVO, outline="")
        self.canvas.create_text(xf, yf, text="FIN",
                                 fill="white", font=("Arial", 11, "bold"))

    def _on_mouse_move(self, event):
        x, y = event.x, event.y

        if self.cursor_id:
            self.canvas.delete(self.cursor_id)
        self.cursor_id = self.canvas.create_oval(
            x-7, y-7, x+7, y+7,
            fill="white", outline=COLOR_TEXTO, width=2)

        if not self.inicio_alcanzado:
            xi, yi = self.waypoints[0]
            if math.hypot(x - xi, y - yi) <= GROSOR_CAMINO:
                self.inicio_alcanzado = True
                self.tiempo_inicio    = time.time()
                self.recorriendo      = True
                self.label_estado.configure(
                    text="Avanza hasta el FIN sin tocar los bordes!",
                    text_color=COLOR_ACCION)
            return

        if not self.recorriendo:
            return

        self.total_muestras += 1
        self.trayectoria.append((x, y))

        dist  = distancia_al_camino(x, y, self.camino_puntos)
        fuera = dist > GROSOR_CAMINO

        if fuera:
            self.muestras_fuera += 1
            if not self._colision_activa:
                self.colisiones += 1
                self._colision_activa = True
                self.label_errores.configure(text=f"Colisiones: {self.colisiones}")
                self.label_estado.configure(text="Saliste del corredor!", text_color=COLOR_ERROR)
                self.after(600, lambda: self.label_estado.configure(
                    text="Vuelve al corredor y sigue hacia el FIN",
                    text_color=COLOR_ALERTA))
            self.canvas.create_oval(x-4, y-4, x+4, y+4,
                                     fill=COLOR_ERROR, outline="")
        else:
            self._colision_activa = False
            self.canvas.create_oval(x-2, y-2, x+2, y+2,
                                     fill="#93C5FD", outline="")
            xf, yf = self.waypoints[-1]
            if math.hypot(x - xf, y - yf) <= GROSOR_CAMINO:
                self._finalizar_laberinto()

    def _on_click(self, event):
        if self.recorriendo:
            xf, yf = self.waypoints[-1]
            if math.hypot(event.x - xf, event.y - yf) <= GROSOR_CAMINO + 10:
                self._finalizar_laberinto()

    def _finalizar_laberinto(self):
        if not self.recorriendo:
            return
        self.recorriendo = False
        self.tiempo_fin  = time.time()

        duracion  = (self.tiempo_fin - self.tiempo_inicio) * 1000
        pct_fuera = (self.muestras_fuera / self.total_muestras * 100) if self.total_muestras > 0 else 0
        dif       = dificultad_para_laberinto(self.laberinto_actual, self.num_laberintos)

        resultado = {
            "laberinto":            self.laberinto_actual + 1,
            "dificultad":           dif,
            "duracion_ms":          round(duracion, 2),
            "colisiones":           self.colisiones,
            "muestras_totales":     self.total_muestras,
            "muestras_fuera":       self.muestras_fuera,
            "porcentaje_fuera":     round(pct_fuera, 2),
            "ruido_motor_estimado": round(pct_fuera * 0.1 + self.colisiones * 0.5, 3)
        }
        self.resultados_laberintos.append(resultado)
        self.laberinto_actual += 1

        if self.laberinto_actual < self.num_laberintos:
            self._pantalla_entre_laberintos(resultado)
        else:
            self.finalizar_test()

    def _pantalla_entre_laberintos(self, resultado):
        self.limpiar_ventana()
        frame = self.crear_tarjeta_centrada(relwidth=0.60, relheight=0.65)

        ctk.CTkLabel(frame,
                     text=f"Laberinto {resultado['laberinto']} completado",
                     font=FUENTE_TITULO, text_color=COLOR_TEXTO).pack(pady=(32, 18))

        res_box = ctk.CTkFrame(frame, fg_color="#0B1220", corner_radius=20)
        res_box.pack(padx=36, pady=10, fill="x")

        for item in [
            f"Tiempo: {resultado['duracion_ms']} ms",
            f"Colisiones: {resultado['colisiones']}",
            f"Fuera del corredor: {resultado['porcentaje_fuera']}%",
        ]:
            ctk.CTkLabel(res_box, text=item,
                         font=("Arial", 20, "bold"),
                         text_color=COLOR_TEXTO).pack(pady=8, padx=20, anchor="center")

        dif_sig = dificultad_para_laberinto(self.laberinto_actual, self.num_laberintos)
        dif_txt = {1: "Facil", 2: "Medio", 3: "Dificil"}.get(dif_sig, "")

        ctk.CTkLabel(
            frame,
            text=f"Siguiente: Laberinto {self.laberinto_actual + 1} / {self.num_laberintos}  -  {dif_txt}",
            font=FUENTE_TEXTO_GRANDE, text_color=COLOR_ALERTA
        ).pack(pady=(20, 12))

        self.crear_boton_principal(frame, "Continuar",
                                   self.iniciar_cuenta_regresiva,
                                   width=280).pack(pady=12)

    # ----------------------------
    # ARCHIVOS
    # ----------------------------
    def guardar_json(self, data):
        os.makedirs("results", exist_ok=True)
        nombre = (f"results/estabilidad_{self.id_paciente}_"
                  f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(nombre, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return nombre

    def generar_pdf(self, data):
        os.makedirs("results", exist_ok=True)
        nombre_pdf = (f"results/informe_estabilidad_{self.id_paciente}_"
                      f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

        c = pdf_canvas.Canvas(nombre_pdf, pagesize=A4)
        ap, al = A4
        y = al - 2*cm

        c.setFont("Helvetica-Bold", 18)
        c.drawString(2*cm, y, "Informe de Evaluacion - Test de Estabilidad Motora")
        y -= 1*cm

        c.setFont("Helvetica", 12)
        c.drawString(2*cm, y, f"Paciente: {data['id_paciente']}")
        y -= 0.7*cm
        c.drawString(2*cm, y, f"Fecha: {data['fecha']}")
        y -= 0.7*cm
        c.drawString(2*cm, y, f"Laberintos completados: {data['resumen']['total_laberintos']}")
        y -= 1*cm

        c.setFont("Helvetica-Bold", 13)
        c.drawString(2*cm, y, "Resumen general")
        y -= 0.8*cm

        res = data["resumen"]
        c.setFont("Helvetica", 12)
        for linea in [
            f"Total colisiones: {res['total_colisiones']}",
            f"Tiempo total: {res['tiempo_total_ms']} ms",
            f"Promedio tiempo fuera: {res['promedio_porcentaje_fuera']}%",
            f"Indice ruido motor global: {res['indice_ruido_motor']}",
        ]:
            c.drawString(2*cm, y, linea); y -= 0.6*cm

        y -= 0.4*cm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2*cm, y, "Detalle por laberinto")
        y -= 0.8*cm

        c.setFont("Helvetica", 11)
        dn = {1: "Facil", 2: "Medio", 3: "Dificil"}
        for lab in data["laberintos"]:
            linea = (
                f"Lab {lab['laberinto']} [{dn.get(lab['dificultad'], '?')}]: "
                f"tiempo {lab['duracion_ms']} ms | "
                f"colisiones {lab['colisiones']} | "
                f"fuera {lab['porcentaje_fuera']}% | "
                f"ruido {lab['ruido_motor_estimado']}"
            )
            c.drawString(2*cm, y, linea); y -= 0.6*cm
            if y < 2*cm:
                c.showPage(); y = al - 2*cm; c.setFont("Helvetica", 11)

        y -= 0.5*cm
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(2*cm, y, "Informe generado automaticamente por OpenRehab ACV.")
        
        y -= 0.8*cm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2*cm, y, "Observaciones clínicas")
        y -= 0.8*cm

        c.setFont("Helvetica-Oblique", 10)
        # Dividimos el texto largo en líneas para que no se corte
        obs_texto = data.get("observaciones", "Sin observaciones.")
        max_chars = 110  # caracteres por línea aprox. en A4
        palabras  = obs_texto.split()
        linea_actual = ""
        for palabra in palabras:
            if len(linea_actual) + len(palabra) + 1 <= max_chars:
                linea_actual += (" " if linea_actual else "") + palabra
            else:
                c.drawString(2*cm, y, linea_actual)
                y -= 0.5*cm
                if y < 2*cm:
                    c.showPage(); y = al - 2*cm; c.setFont("Helvetica-Oblique", 10)
                linea_actual = palabra
        if linea_actual:
            c.drawString(2*cm, y, linea_actual)
            y -= 0.5*cm
        c.save()
        return nombre_pdf

    def generar_observaciones(self, data):
        """
    Analiza los resultados del test de laberinto y genera observaciones clínicas
    basadas en los umbrales patológicos definidos por el estudio de referencia.

    Umbrales patológicos:
      - Tiempo por laberinto: > 20000 ms (fácil), > 30000 ms (medio), > 40000 ms (difícil)
      - Colisiones por laberinto: >= 9
      - Porcentaje de tiempo fuera del camino: >= 15%
      - Índice de ruido motor global: > 5
    """
        observaciones = []
        nombres_dificultad = {1: "fácil", 2: "medio", 3: "difícil"}
        umbrales_tiempo    = {1: 20000,   2: 30000,   3: 40000}

        # ── Análisis por laberinto ──────────────────────────────────────────────
        labs_tiempo_pat   = []
        labs_colision_pat = []
        labs_fuera_pat    = []

        for lab in data["laberintos"]:
            dif   = lab["dificultad"]
            umbral = umbrales_tiempo.get(dif, 20000)

            if lab["duracion_ms"] > umbral:
                labs_tiempo_pat.append(
                    f"Laberinto {lab['laberinto']} ({nombres_dificultad[dif]}): "
                    f"{lab['duracion_ms']} ms (umbral: {umbral} ms)"
                )

            if lab["colisiones"] >= 9:
                labs_colision_pat.append(
                    f"Laberinto {lab['laberinto']}: {lab['colisiones']} colisiones"
                )

            if lab["porcentaje_fuera"] >= 15.0:
                labs_fuera_pat.append(
                    f"Laberinto {lab['laberinto']}: {lab['porcentaje_fuera']}% fuera del corredor"
                )

        # ── Observaciones de tiempo ─────────────────────────────────────────────
        if labs_tiempo_pat:
            detalle = "; ".join(labs_tiempo_pat)
            observaciones.append(
                f"Tiempo de ejecución patológico en {len(labs_tiempo_pat)} laberinto(s): {detalle}. "
                "Puede indicar lentitud motora o dificultad para planificar el movimiento."
            )
        else:
            observaciones.append(
                "Los tiempos de ejecución se encuentran dentro de los rangos esperados para cada nivel de dificultad."
            )

        # ── Observaciones de colisiones ─────────────────────────────────────────
        total_col = data["resumen"]["total_colisiones"]
        if labs_colision_pat:
            detalle = "; ".join(labs_colision_pat)
            observaciones.append(
                f"Se registraron 9 o más colisiones en {len(labs_colision_pat)} laberinto(s): {detalle}. "
                "Esto sugiere dificultad en el control de trayectoria y posible déficit de coordinación visomotora."
            )
        elif total_col > 0:
            observaciones.append(
                f"Se registraron {total_col} colisión/es en total, sin superar el umbral patológico por laberinto."
            )
        else:
            observaciones.append("No se registraron colisiones durante la sesión.")

        # ── Observaciones de porcentaje fuera del corredor ──────────────────────
        if labs_fuera_pat:
            detalle = "; ".join(labs_fuera_pat)
            observaciones.append(
                f"Porcentaje de tiempo fuera del corredor patológico (≥ 15%) en "
                f"{len(labs_fuera_pat)} laberinto(s): {detalle}. "
                "Indica dificultad para mantener el cursor dentro del trayecto requerido."
            )
        else:
            pct_prom = data["resumen"]["promedio_porcentaje_fuera"]
            observaciones.append(
                f"El porcentaje promedio de tiempo fuera del corredor fue de {pct_prom}%, "
                "dentro del rango normal (< 15%)."
            )

        # ── Observaciones del índice de ruido motor global ──────────────────────
        ruido = data["resumen"]["indice_ruido_motor"]
        if ruido > 5:
            observaciones.append(
                f"El índice de ruido motor global es {ruido}, superando el umbral patológico de 5. "
                "Este resultado es consistente con presencia de temblor, espasticidad u otro componente de inestabilidad motora."
            )
        else:
            observaciones.append(
                f"El índice de ruido motor global es {ruido}, dentro del rango normal (≤ 5)."
            )

        # ── Conclusión general ───────────────────────────────────────────────────
        indicadores_pat = sum([
            bool(labs_tiempo_pat),
            bool(labs_colision_pat),
            bool(labs_fuera_pat),
            ruido > 5
        ])

        if indicadores_pat == 0:
            observaciones.append(
                "Conclusión: el paciente presentó un desempeño general dentro de los parámetros normales."
            )
        elif indicadores_pat == 1:
            observaciones.append(
                "Conclusión: se detectó un indicador fuera del rango normal. Se recomienda seguimiento clínico."
            )
        elif indicadores_pat == 2:
            observaciones.append(
                "Conclusión: se detectaron dos indicadores patológicos. Se sugiere evaluación clínica complementaria."
            )
        else:
            observaciones.append(
                "Conclusión: múltiples indicadores patológicos. Se recomienda derivación a especialista para evaluación motora detallada."
            )

        return " ".join(observaciones)

    # ----------------------------
    # FINALIZACION
    # ----------------------------
    def finalizar_test(self):
        n          = len(self.resultados_laberintos)
        total_col  = sum(r["colisiones"]           for r in self.resultados_laberintos)
        t_total    = sum(r["duracion_ms"]           for r in self.resultados_laberintos)
        pct_prom   = sum(r["porcentaje_fuera"]      for r in self.resultados_laberintos) / n
        ruido      = round(sum(r["ruido_motor_estimado"] for r in self.resultados_laberintos) / n, 3)

        data = {
            "id_paciente": self.id_paciente,
            "fecha":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "laberintos":  self.resultados_laberintos,
            "resumen": {
                "total_laberintos":         n,
                "total_colisiones":         total_col,
                "tiempo_total_ms":          round(t_total, 2),
                "promedio_porcentaje_fuera": round(pct_prom, 2),
                "indice_ruido_motor":        ruido
            }
        }
        data["observaciones"] = self.generar_observaciones(data)
        self.archivo_json = self.guardar_json(data)
        self.archivo_pdf  = self.generar_pdf(data)
        self.mostrar_pantalla_final(data)

    def mostrar_pantalla_final(self, data):
        self.limpiar_ventana()
        frame = self.crear_tarjeta_centrada(relwidth=0.65, relheight=0.84)

        ctk.CTkLabel(frame, text="Evaluacion finalizada",
                     font=FUENTE_TITULO, text_color=COLOR_TEXTO).pack(pady=(28, 18))

        res_box = ctk.CTkFrame(frame, fg_color="#0B1220", corner_radius=20)
        res_box.pack(padx=36, pady=10, fill="x")

        res = data["resumen"]
        for item in [
            f"Paciente: {self.id_paciente}",
            f"Laberintos completados: {res['total_laberintos']}",
            f"Total colisiones: {res['total_colisiones']}",
            f"Tiempo total: {res['tiempo_total_ms']} ms",
            f"Tiempo promedio fuera del corredor: {res['promedio_porcentaje_fuera']}%",
            f"Indice de ruido motor: {res['indice_ruido_motor']}",
        ]:
            ctk.CTkLabel(res_box, text=item,
                         font=("Arial", 19, "bold"),
                         text_color=COLOR_TEXTO).pack(pady=6, padx=20, anchor="center")

        ctk.CTkLabel(frame, text="Los informes fueron guardados correctamente.",
                     font=FUENTE_TEXTO_GRANDE,
                     text_color=COLOR_ACCION).pack(pady=(20, 8))

        ctk.CTkLabel(frame, text=f"PDF: {self.archivo_pdf}",
                     font=("Arial", 13), text_color=COLOR_SUBTEXTO,
                     wraplength=620, justify="center").pack(pady=2)

        ctk.CTkLabel(frame, text=f"JSON: {self.archivo_json}",
                     font=("Arial", 13), text_color=COLOR_SUBTEXTO,
                     wraplength=620, justify="center").pack(pady=2)

        self.crear_boton_principal(
            frame, "Abrir informe PDF",
            lambda: self.abrir_archivo(self.archivo_pdf),
            color="#3B82F6", hover="#2563EB", width=300).pack(pady=(16, 8))

        self.crear_boton_principal(
            frame,
            "Volver al menú",
            lambda: menu.crear_pantalla_menu(self.parent),
            width=300
        ).pack(pady=10)

# ----------------------------
# EJECUCION
# ----------------------------