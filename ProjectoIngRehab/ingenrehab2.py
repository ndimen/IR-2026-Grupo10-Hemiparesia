import customtkinter as ctk
import tkinter as tk
import random
import math
import json
import os
import time
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
import platform
import subprocess
import menu # <--- IMPORTAMOS EL NUEVO ARCHIVO DEL MENÚ


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ANCHO = 1100
ALTO = 760
NUM_INTENTOS = 10

COLOR_FONDO = "#0F172A"       # azul oscuro
COLOR_PANEL = "#1E293B"       # panel
COLOR_PANEL_2 = "#334155"     # panel secundario
COLOR_TEXTO = "#F8FAFC"       # casi blanco
COLOR_SUBTEXTO = "#CBD5E1"    # gris claro
COLOR_ACCION = "#22C55E"      # verde
COLOR_ACCION_HOVER = "#16A34A"
COLOR_ALERTA = "#F59E0B"      # ámbar
COLOR_ERROR = "#EF4444"       # rojo
COLOR_OBJETIVO = "#F97316"    # naranja fuerte
COLOR_OBJETIVO_BORDE = "#FDBA74"

FUENTE_TITULO = ("Arial", 30, "bold")
FUENTE_SUBTITULO = ("Arial", 20, "bold")
FUENTE_TEXTO = ("Arial", 18)
FUENTE_TEXTO_GRANDE = ("Arial", 22, "bold")
FUENTE_BOTON = ("Arial", 18, "bold")

# ----------------------------
# APP
# ----------------------------
class FittsApp(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#0F172A")
        self.id_paciente = parent.id_paciente
        self.nombre_paciente = parent.nombre_paciente
        
        self.configure(fg_color=COLOR_FONDO)

        self.id_paciente = ""
        self.entry_paciente = None
        self.intento_actual = 0
        self.aciertos = 0
        self.errores = 0
        self.resultados = []

        self.obj_x = None
        self.obj_y = None
        self.obj_r = None
        self.obj_anterior = None
        self.tiempo_inicio = None

        self.archivo_json = None
        self.archivo_pdf = None

        self.crear_pantalla_inicio()

    def iniciar_cuenta_regresiva(self):
        self.limpiar_ventana()

        self.countdown_frame = self.crear_tarjeta_centrada(relwidth=0.55, relheight=0.55)

        self.countdown_label = ctk.CTkLabel(
            self.countdown_frame,
            text="3",
            font=("Arial", 90, "bold"),
            text_color=COLOR_ALERTA
        )
        self.countdown_label.pack(expand=True)

        self.after(1000, lambda: self.actualizar_cuenta_regresiva(2))

    def actualizar_cuenta_regresiva(self, numero):
        if numero > 0:
            self.countdown_label.configure(text=str(numero))
            self.after(1000, lambda: self.actualizar_cuenta_regresiva(numero - 1))
        else:
            self.countdown_label.configure(text="¡Comienza!", text_color=COLOR_ACCION)
            self.after(800, self.comenzar_evaluacion_real)

    def crear_pantalla_listo(self):
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
            text="Toque el círculo naranja lo más rápido y preciso posible.",
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
            self.crear_pantalla_instrucciones,
            color="#64748B",
            hover="#475569",
            width=280
        ).pack(pady=12)

    def validar_dni(self, dni):
        dni = dni.strip()

        if dni == "":
            return False, "Por favor, ingresá el DNI."

        if not dni.isdigit():
            return False, "Error: el DNI debe contener solo números."

        if len(dni) not in [7, 8]:
            return False, "Error: el DNI es erroneo."

        return True, ""

    # ----------------------------
    # UTILIDADES
    # ----------------------------
    def limpiar_ventana(self):
        for widget in self.winfo_children():
            widget.destroy()

    def distancia(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def calcular_id_fitts(self, D, W):
        if W <= 0:
            return 0
        return math.log2((D / W) + 1)

    def abrir_carpeta_resultados(self):
        carpeta = os.path.abspath("results")
        os.makedirs(carpeta, exist_ok=True)

        try:
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(carpeta)
            elif sistema == "Darwin":
                subprocess.run(["open", carpeta])
            else:
                subprocess.run(["xdg-open", carpeta])
        except Exception as e:
            print("No se pudo abrir la carpeta:", e)

    def abrir_archivo(self, ruta):
        try:
            ruta_abs = os.path.abspath(ruta)
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(ruta_abs)
            elif sistema == "Darwin":
                subprocess.run(["open", ruta_abs])
            else:
                subprocess.run(["xdg-open", ruta_abs])
        except Exception as e:
            print("No se pudo abrir el archivo:", e)

    def crear_tarjeta_centrada(self, relwidth=0.68, relheight=0.74):
        frame = ctk.CTkFrame(
            self,
            corner_radius=24,
            fg_color=COLOR_PANEL,
            border_width=2,
            border_color=COLOR_PANEL_2
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=relwidth, relheight=relheight)
        return frame

    def crear_boton_principal(self, master, text, command, color=COLOR_ACCION, hover=COLOR_ACCION_HOVER, width=260):
        return ctk.CTkButton(
            master,
            text=text,
            command=command,
            width=width,
            height=54,
            corner_radius=16,
            fg_color=color,
            hover_color=hover,
            text_color=COLOR_TEXTO,
            font=FUENTE_BOTON
        )

    # ----------------------------
    # PANTALLA INICIAL
    # ----------------------------
   # ----------------------------
    # PANTALLA INICIAL (LIMPIA)
    # ----------------------------
    def crear_pantalla_inicio(self):
        self.limpiar_ventana()

        frame = self.crear_tarjeta_centrada(relwidth=0.62, relheight=0.75)

        ctk.CTkLabel(
            frame,
            text="OpenRehab ACV",
            font=("Arial", 18, "bold"),
            text_color=COLOR_SUBTEXTO
        ).pack(pady=(18, 8))

        ctk.CTkLabel(
            frame,
            text="Prueba de Ley de Fitts",
            font=FUENTE_TITULO,
            text_color=COLOR_TEXTO
        ).pack(pady=(0, 10))

        # Mostramos el paciente que ya inició sesión
        ctk.CTkLabel(
            frame,
            text=f"Jugador actual: {self.nombre_paciente} (DNI: {self.id_paciente})",
            font=("Arial", 18, "bold"),
            text_color=COLOR_ACCION
        ).pack(pady=(10, 20))

        texto_simple = (
            "Esta prueba consiste en tocar círculos en la pantalla.\n"
            "Se busca medir rapidez y precisión.\n\n"
        )

        ctk.CTkLabel(
            frame,
            text=texto_simple,
            font=FUENTE_TEXTO,
            justify="center",
            text_color=COLOR_SUBTEXTO
        ).pack(pady=(10, 30))

        self.crear_boton_principal(
            frame,
            "Ver instrucciones",
            self.crear_pantalla_instrucciones, # Va directo a las instrucciones
            color="#3B82F6",
            hover="#2563EB"
        ).pack(pady=10)

        self.crear_boton_principal(
            frame,
            "Comenzar evaluación",
            self.iniciar_test
        ).pack(pady=10)

        self.crear_boton_principal(
            frame,
            "Volver al Menú",
            lambda: menu.crear_pantalla_menu(self),
            color="#64748B",
            hover="#475569"
        ).pack(pady=10)
        
    # ----------------------------    
    # INSTRUCCIONES
    # ----------------------------
    def crear_pantalla_instrucciones(self):
        self.limpiar_ventana()

        frame = self.crear_tarjeta_centrada(relwidth=0.72, relheight=0.82)

        ctk.CTkLabel(
            frame,
            text="Instrucciones",
            font=FUENTE_TITULO,
            text_color=COLOR_TEXTO
        ).pack(pady=(28, 18))

        bloque = ctk.CTkFrame(frame, fg_color="#0B1220", corner_radius=20)
        bloque.pack(padx=40, pady=10, fill="both", expand=False)

        texto = (
            "1. Va a aparecer un círculo naranja.\n\n"
            "2. Tocá el círculo con un clic.\n\n"
            "3. Después aparecerá otro círculo en otro lugar.\n\n"
            "4. Repetí hasta terminar todos los intentos.\n\n"
            "Importante:\n"
            "• Hacelo lo más rápido posible.\n"
            "• Tratá de no errarle.\n"
            "• Si hacés clic fuera del círculo, cuenta como error.\n\n"
            "Al finalizar:\n"
            "• Se generará un informe PDF."
        )

        ctk.CTkLabel(
            bloque,
            text=texto,
            font=("Arial", 20),
            justify="left",
            text_color=COLOR_TEXTO,
            wraplength=650
        ).pack(padx=28, pady=28)

        ctk.CTkLabel(
            frame,
            text="Cuando estés listo/a, presioná comenzar.",
            font=FUENTE_TEXTO_GRANDE,
            text_color=COLOR_ALERTA
        ).pack(pady=(20, 18))

        self.crear_boton_principal(
            frame,
            "Comenzar",
            self.iniciar_test,
            width=280
        ).pack(pady=10)

        self.crear_boton_principal(
            frame,
            "Volver",
            self.crear_pantalla_inicio,
            color="#64748B",
            hover="#475569",
            width=280
        ).pack(pady=10)

    # ----------------------------
    # TEST
    # ----------------------------
    def iniciar_test(self):
        self.crear_pantalla_listo()

    def comenzar_evaluacion_real(self):
        self.intento_actual = 1
        self.aciertos = 0
        self.errores = 0
        self.resultados = []
        self.obj_anterior = None
        self.archivo_json = None
        self.archivo_pdf = None

        self.crear_pantalla_test()
        self.generar_objetivo()

    def crear_pantalla_test(self):
        self.limpiar_ventana()

        self.top_frame = ctk.CTkFrame(self, height=120, corner_radius=0, fg_color=COLOR_PANEL)
        self.top_frame.pack(fill="x")

        self.info_box = ctk.CTkFrame(self.top_frame, fg_color=COLOR_PANEL, corner_radius=0)
        self.info_box.pack(fill="both", expand=True, padx=24, pady=16)

        self.label_paciente = ctk.CTkLabel(
            self.info_box,
            text=f"Paciente: {self.id_paciente}",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_paciente.grid(row=0, column=0, padx=10, pady=6, sticky="w")

        self.label_intento = ctk.CTkLabel(
            self.info_box,
            text=f"Intento {self.intento_actual} de {NUM_INTENTOS}",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_intento.grid(row=0, column=1, padx=10, pady=6)

        self.label_errores = ctk.CTkLabel(
            self.info_box,
            text=f"Errores: {self.errores}",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_errores.grid(row=0, column=2, padx=10, pady=6, sticky="e")

        self.label_estado = ctk.CTkLabel(
            self.info_box,
            text="Tocá el círculo naranja",
            font=("Arial", 24, "bold"),
            text_color=COLOR_ALERTA
        )
        self.label_estado.grid(row=1, column=0, columnspan=3, pady=(8, 0))

        self.info_box.grid_columnconfigure(0, weight=1)
        self.info_box.grid_columnconfigure(1, weight=1)
        self.info_box.grid_columnconfigure(2, weight=1)

        self.canvas = tk.Canvas(
            self,
            width=ANCHO,
            height=ALTO - 120,
            bg=COLOR_FONDO,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.click_canvas)

    def generar_objetivo(self):
        self.canvas.delete("all")

        radios = [35, 45, 55, 65]
        self.obj_r = random.choice(radios)

        margen = self.obj_r + 30

        while True:
            self.obj_x = random.randint(margen, ANCHO - margen)
            self.obj_y = random.randint(margen, (ALTO - 120) - margen)

            if self.obj_anterior is None:
                break
            d = self.distancia((self.obj_x, self.obj_y), self.obj_anterior)
            if d > 220:
                break

        self.canvas.create_oval(
            self.obj_x - self.obj_r - 10,
            self.obj_y - self.obj_r - 10,
            self.obj_x + self.obj_r + 10,
            self.obj_y + self.obj_r + 10,
            fill=COLOR_OBJETIVO_BORDE,
            outline=""
        )

        self.canvas.create_oval(
            self.obj_x - self.obj_r,
            self.obj_y - self.obj_r,
            self.obj_x + self.obj_r,
            self.obj_y + self.obj_r,
            fill=COLOR_OBJETIVO,
            outline=""
        )

        self.tiempo_inicio = time.time()

    def click_canvas(self, event):
        dx = event.x - self.obj_x
        dy = event.y - self.obj_y
        d_click = math.sqrt(dx**2 + dy**2)

        if d_click <= self.obj_r:
            tiempo_ms = (time.time() - self.tiempo_inicio) * 1000

            if self.obj_anterior is None:
                D = 0
            else:
                D = self.distancia((self.obj_x, self.obj_y), self.obj_anterior)

            W = self.obj_r * 2
            ID = self.calcular_id_fitts(D, W) if D > 0 else 0

            self.resultados.append({
                "intento": self.intento_actual,
                "objetivo_x": self.obj_x,
                "objetivo_y": self.obj_y,
                "radio": self.obj_r,
                "distancia_desde_anterior_px": round(D, 2),
                "ancho_objetivo_px": W,
                "indice_dificultad": round(ID, 3),
                "tiempo_ms": round(tiempo_ms, 2),
                "acierto": True
            })

            self.aciertos += 1
            self.obj_anterior = (self.obj_x, self.obj_y)
            self.intento_actual += 1

            if self.intento_actual > NUM_INTENTOS:
                self.finalizar_test()
            else:
                self.label_intento.configure(text=f"Intento {self.intento_actual} de {NUM_INTENTOS}")
                self.label_estado.configure(text="Muy bien. Tocá el siguiente círculo.", text_color=COLOR_ACCION)
                self.after(350, lambda: self.label_estado.configure(text="Tocá el círculo naranja", text_color=COLOR_ALERTA))
                self.generar_objetivo()

        else:
            self.errores += 1
            self.label_errores.configure(text=f"Errores: {self.errores}")
            self.label_estado.configure(text="Ese clic quedó fuera del círculo", text_color=COLOR_ERROR)
            self.after(700, lambda: self.label_estado.configure(text="Tocá el círculo naranja", text_color=COLOR_ALERTA))

    # ----------------------------
    # ARCHIVOS
    # ----------------------------
    def guardar_json(self, data):
        os.makedirs("results", exist_ok=True)
        nombre = f"results/fitts_{self.id_paciente}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(nombre, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return nombre

    def generar_pdf(self, data):
        os.makedirs("results", exist_ok=True)
        nombre_pdf = f"results/informe_fitts_{self.id_paciente}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        c = pdf_canvas.Canvas(nombre_pdf, pagesize=A4)
        ancho, alto = A4
        y = alto - 2 * cm

        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, y, "Informe de Evaluación - Ley de Fitts")
        y -= 1 * cm

        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, f"Paciente: {data['id_paciente']}")
        y -= 0.7 * cm
        c.drawString(2 * cm, y, f"Fecha: {data['fecha']}")
        y -= 1 * cm

        c.setFont("Helvetica-Bold", 13)
        c.drawString(2 * cm, y, "Resumen")
        y -= 0.8 * cm

        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, f"Intentos: {data['resumen']['cantidad_intentos']}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Aciertos: {data['resumen']['aciertos']}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Errores: {data['resumen']['errores']}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Tiempo promedio: {data['resumen']['tiempo_promedio_ms']} ms")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Indice de dificultad promedio: {data['resumen']['indice_dificultad_promedio']}")
        y -= 1 * cm

        c.setFont("Helvetica-Bold", 13)
        c.drawString(2 * cm, y, "Detalle por intento")
        y -= 0.8 * cm

        c.setFont("Helvetica", 10)
        for r in data["intentos"]:
            linea = (
                f"Intento {r['intento']}: tiempo {r['tiempo_ms']} ms | "
                f"radio {r['radio']} px | distancia {r['distancia_desde_anterior_px']} px | "
                f"ID {r['indice_dificultad']}"
            )
            c.drawString(2 * cm, y, linea)
            y -= 0.5 * cm

            if y < 2 * cm:
                c.showPage()
                y = alto - 2 * cm
                c.setFont("Helvetica", 10)

        y -= 0.5 * cm
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(2 * cm, y, "Informe generado automaticamente por el modulo en Python.")
        c.save()

        return nombre_pdf

    # ----------------------------
    # FIN
    # ----------------------------
    def finalizar_test(self):
        tiempos = [r["tiempo_ms"] for r in self.resultados]
        ids = [r["indice_dificultad"] for r in self.resultados if r["indice_dificultad"] > 0]

        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
        id_promedio = sum(ids) / len(ids) if ids else 0

        data = {
            "id_paciente": self.id_paciente,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "métrica_principal": round(tiempo_promedio, 2),
            "unidad": "ms",
            "intentos": self.resultados,
            "resumen": {
                "cantidad_intentos": NUM_INTENTOS,
                "aciertos": self.aciertos,
                "errores": self.errores,
                "tiempo_promedio_ms": round(tiempo_promedio, 2),
                "indice_dificultad_promedio": round(id_promedio, 3)
            }
        }

        self.archivo_json = self.guardar_json(data)
        self.archivo_pdf = self.generar_pdf(data)
        self.mostrar_pantalla_final(data)

    def mostrar_pantalla_final(self, data):
        self.limpiar_ventana()

        frame = self.crear_tarjeta_centrada(relwidth=0.65, relheight=0.8)

        ctk.CTkLabel(
            frame,
            text="Evaluación finalizada",
            font=FUENTE_TITULO,
            text_color=COLOR_TEXTO
        ).pack(pady=(28, 18))

        resumen = ctk.CTkFrame(frame, fg_color="#0B1220", corner_radius=20)
        resumen.pack(padx=36, pady=10, fill="x")

        items = [
            f"Paciente: {self.id_paciente}",
            f"Aciertos: {self.aciertos}",
            f"Errores: {self.errores}",
            f"Tiempo promedio: {data['resumen']['tiempo_promedio_ms']} ms",
            f"Índice de dificultad promedio: {data['resumen']['indice_dificultad_promedio']}"
        ]

        for item in items:
            ctk.CTkLabel(
                resumen,
                text=item,
                font=("Arial", 20, "bold"),
                text_color=COLOR_TEXTO
            ).pack(pady=8, padx=20, anchor="center")

        ctk.CTkLabel(
            frame,
            text="Los informes fueron guardados correctamente.",
            font=FUENTE_TEXTO_GRANDE,
            text_color=COLOR_ACCION
        ).pack(pady=(22, 12))

        ctk.CTkLabel(
            frame,
            text=f"PDF: {self.archivo_pdf}",
            font=("Arial", 14),
            text_color=COLOR_SUBTEXTO,
            wraplength=620,
            justify="center"
        ).pack(pady=4)

        ctk.CTkLabel(
            frame,
            text=f"JSON: {self.archivo_json}",
            font=("Arial", 14),
            text_color=COLOR_SUBTEXTO,
            wraplength=620,
            justify="center"
        ).pack(pady=4)

        self.crear_boton_principal(
            frame,
            "Abrir informe PDF",
            lambda: self.abrir_archivo(self.archivo_pdf),
            color="#3B82F6",
            hover="#2563EB",
            width=300
        ).pack(pady=(18, 10))

        self.crear_boton_principal(
         frame,
         "Volver al menú",
         lambda: menu.crear_pantalla_menu(self),
         width=300
     ).pack(pady=10)

# ----------------------------
# EJECUCIÓN
# ----------------------------