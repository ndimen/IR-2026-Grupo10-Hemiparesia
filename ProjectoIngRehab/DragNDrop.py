import customtkinter as ctk
import tkinter as tk
import random
import math
import time
import os
import json
import platform
import subprocess
from datetime import datetime
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import menu

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ANCHO = 1100
ALTO = 760
NUM_INTENTOS = 8

COLOR_FONDO = "#0F172A"
COLOR_PANEL = "#1E293B"
COLOR_PANEL_2 = "#334155"
COLOR_TEXTO = "#F8FAFC"
COLOR_SUBTEXTO = "#CBD5E1"
COLOR_ACCION = "#22C55E"
COLOR_ACCION_HOVER = "#16A34A"
COLOR_ALERTA = "#F59E0B"
COLOR_ERROR = "#EF4444"
COLOR_OBJ = "#38BDF8"
COLOR_TARGET = "#F97316"
COLOR_TARGET_BORDE = "#FDBA74"

FUENTE_TITULO = ("Arial", 30, "bold")
FUENTE_TEXTO = ("Arial", 18)
FUENTE_TEXTO_GRANDE = ("Arial", 22, "bold")
FUENTE_BOTON = ("Arial", 18, "bold") #misma estructura que la de Fitts para mantener consistencia visual

class DragDropGame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#0F172A")

        self.parent = parent
        self.configure(fg_color=COLOR_FONDO)

        self.id_paciente = parent.id_paciente
        self.nombre_paciente = parent.nombre_paciente

        self.intento = 1
        self.resultados = []
        self.t_inicio = None
        self.dragging = False
        self.timer_running = False

        # CAMBIO CLAVE: En lugar de llamar a self.crear_ui(), 
        # llamamos al login del menú para que identifique al paciente primero.
        self.crear_pantalla_inicio()
        
    def limpiar_ventana(self):
        """Borra todo lo que hay en la pantalla actual"""
        for widget in self.winfo_children():
            widget.destroy()

    def crear_pantalla_inicio(self): #cambie el inicio
        self.limpiar_ventana()

        frame = self.crear_tarjeta_centrada(relwidth=0.62, relheight=0.78)

        ctk.CTkLabel(
            frame,
            text="OpenRehab ACV",
            font=("Arial", 18, "bold"),
            text_color=COLOR_SUBTEXTO
        ).pack(pady=(18, 8))

        ctk.CTkLabel(
            frame,
            text="Prueba de Arrastre y Soltar",
            font=FUENTE_TITULO,
            text_color=COLOR_TEXTO
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text="Evaluación de coordinación y control del movimiento",
            font=FUENTE_TEXTO,
            text_color=COLOR_SUBTEXTO
        ).pack(pady=(0, 24))

        texto_simple = (
            "Esta prueba consiste en arrastrar un círculo azul\n"
            "hasta un objetivo naranja.\n\n"
            "Se busca medir rapidez y precisión del movimiento."
        )

        ctk.CTkLabel(
            frame,
            text=texto_simple,
            font=FUENTE_TEXTO,
            justify="center",
            text_color=COLOR_SUBTEXTO
        ).pack(pady=(20, 40))

        ctk.CTkLabel(
            frame,
            text=f"Paciente: {self.nombre_paciente} | DNI: {self.id_paciente}",
            font=("Arial", 16, "bold"),
            text_color=COLOR_SUBTEXTO
        ).pack(pady=(0, 16))

        self.crear_boton_principal(
            frame,
            "Ver instrucciones",
            self.crear_pantalla_instrucciones,
            color="#3B82F6",
            hover="#2563EB"
        ).pack(pady=10)

        self.crear_boton_principal(
            frame,
            "Comenzar evaluación",
            self.crear_pantalla_listo
        ).pack(pady=10)
        
        self.crear_boton_principal(
            frame,
            "Volver al Menú",
            lambda: menu.crear_pantalla_menu(self.parent),
            color="#64748B",
            hover="#475569"
        ).pack(pady=10)
        
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
            "1. Va a aparecer un círculo azul y un objetivo naranja.\n\n"
            "2. Arrastrá el círculo azul hasta el objetivo naranja.\n\n"
            "3. Soltalo encima del objetivo.\n\n"
            "4. Repetí hasta terminar todos los intentos.\n\n"
            "Importante:\n"
            "• Hacelo lo más rápido posible.\n"
            "• Tratá de ser preciso/a.\n"
            "• Si soltás lejos del objetivo, cuenta como intento fallido.\n\n"
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
            self.crear_pantalla_listo,
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
            text="Arrastre el círculo azul hacia el objetivo naranja lo más rápido y preciso posible.",
            font=("Arial", 20, "bold"),
            text_color=COLOR_ALERTA,
            justify="center",
            wraplength=600
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
            self.after(800, self.crear_ui)

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
    def crear_ui(self):
        self.limpiar_ventana()

        self.top = ctk.CTkFrame(self, height=120, corner_radius=0, fg_color=COLOR_PANEL)
        self.top.pack(fill="x")

        self.info_box = ctk.CTkFrame(self.top, fg_color=COLOR_PANEL, corner_radius=0)
        self.info_box.pack(fill="both", expand=True, padx=24, pady=16)

        self.label_paciente = ctk.CTkLabel(
            self.info_box,
            text=f"Paciente: {self.nombre_paciente}",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_paciente.grid(row=0, column=0, padx=10, pady=6, sticky="w")

        self.label_intento = ctk.CTkLabel(
            self.info_box,
            text=f"Intento {self.intento} de {NUM_INTENTOS}",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_intento.grid(row=0, column=1, padx=10, pady=6)

        self.label_tiempo = ctk.CTkLabel(
            self.info_box,
            text="Tiempo: 0 ms",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_tiempo.grid(row=0, column=2, padx=10, pady=6, sticky="e")

        self.label_instr = ctk.CTkLabel(
            self.info_box,
            text="Arrastrá el círculo azul al objetivo naranja",
            font=("Arial", 24, "bold"),
            text_color=COLOR_ALERTA
        )
        self.label_instr.grid(row=1, column=0, columnspan=3, pady=(8, 0))

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

        self.canvas.bind("<ButtonPress-1>", self.iniciar_drag)
        self.canvas.bind("<B1-Motion>", self.arrastrar)
        self.canvas.bind("<ButtonRelease-1>", self.soltar)

        self.generar_escenario()
    # ----------------------------
    def distancia(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    # ----------------------------
    def abrir_archivo(self, ruta):
        try:
            ruta = os.path.abspath(ruta)
            print("Intentando abrir:", ruta)

            if not os.path.exists(ruta):
                print("ERROR: el archivo no existe")
                return

            sistema = platform.system()

            if sistema == "Windows":
                os.startfile(ruta)
            elif sistema == "Darwin":
                subprocess.run(["open", ruta])
            else:
                subprocess.run(["xdg-open", ruta])

        except Exception as e:
            print("Error al abrir archivo:", e)

    # ----------------------------
    def generar_escenario(self):
        self.canvas.delete("all")

        radio = 40
        margen = 80

        while True:
            self.obj_x = random.randint(margen, ANCHO-margen)
            self.obj_y = random.randint(margen, ALTO-100-margen)

            self.target_x = random.randint(margen, ANCHO-margen)
            self.target_y = random.randint(margen, ALTO-100-margen)

            if self.distancia(
                (self.obj_x, self.obj_y),
                (self.target_x, self.target_y)
            ) > 300:
                break

        self.canvas.create_oval(
            self.target_x-radio-10,
            self.target_y-radio-10,
            self.target_x+radio+10,
            self.target_y+radio+10,
            fill=COLOR_TARGET_BORDE,
            outline=""
        )

        self.target = self.canvas.create_oval(
            self.target_x-radio,
            self.target_y-radio,
            self.target_x+radio,
            self.target_y+radio,
            fill=COLOR_TARGET,
            outline=""
        )
        

        self.obj = self.canvas.create_oval(
            self.obj_x-radio,
            self.obj_y-radio,
            self.obj_x+radio,
            self.obj_y+radio,
            fill=COLOR_OBJ
        )

        self.t_inicio = time.time()

        if not self.timer_running:
            self.timer_running = True
            self.actualizar_tiempo()

    # ----------------------------
    def actualizar_tiempo(self):
        if self.t_inicio:
            tiempo = (time.time() - self.t_inicio) * 1000
            self.label_tiempo.configure(text=f"Tiempo: {int(tiempo)} ms")

        if self.timer_running:
            self.after(50, self.actualizar_tiempo)

    # ----------------------------
    def iniciar_drag(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if self.obj in items:
            self.dragging = True
    def generar_observaciones(self, promedio):
        if promedio == 0:
            return "No se registraron aciertos."

        if promedio > 800:
            return "Tiempo de reacción elevado. Posible dificultad motora o fatiga."

        if promedio > 500:
            return "Rendimiento medio con leve fatiga en intentos finales."

        return "Buen rendimiento general, tiempos de reacción adecuados."
    # ----------------------------
    def arrastrar(self, event):
        if self.dragging:
            self.canvas.coords(
                self.obj,
                event.x-40, event.y-40,
                event.x+40, event.y+40
            )

    # ----------------------------
    def soltar(self, event):
        if not self.dragging:
            return

        self.dragging = False

        tiempo = (time.time() - self.t_inicio) * 1000

        dist = self.distancia(
            (event.x, event.y),
            (self.target_x, self.target_y)
        )

        exito = dist < 50

        self.resultados.append({
            "intento": self.intento,
            "tiempo_ms": round(tiempo, 2),
            "exito": exito
        })

        if self.intento == NUM_INTENTOS:
            self.finalizar()
            return

        self.intento += 1
        self.label_intento.configure(text=f"Intento {self.intento}/{NUM_INTENTOS}")
        self.generar_escenario()

    # ----------------------------
    def guardar_json(self, data):
        os.makedirs("results", exist_ok=True)
        nombre = f"results/drag_{self.id_paciente}_{datetime.now().strftime('%H%M%S')}.json"

        with open(nombre, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return nombre

    # ----------------------------
    def generar_pdf(self, data):
        os.makedirs("results", exist_ok=True)
        nombre = f"results/drag_{self.id_paciente}_{datetime.now().strftime('%H%M%S')}.pdf"

        c = pdf_canvas.Canvas(nombre, pagesize=A4)
        y = 800

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Informe Drag & Drop")
        y -= 40

        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Paciente: {self.id_paciente}")
        y -= 30

        for r in data["intentos"]:
            linea = f"Intento {r['intento']} - tiempo: {r['tiempo_ms']} ms - exito: {r['exito']}"
            c.drawString(50, y, linea)
            y -= 20

        c.save()
        return nombre

    # ----------------------------
    def finalizar(self):
        print("FINALIZANDO JUEGO")

        self.timer_running = False

        # ----------------------------
        # PROCESAMIENTO DE DATOS
        # ----------------------------
        tiempos_validos = [r["tiempo_ms"] for r in self.resultados if r["exito"]]

        promedio = sum(tiempos_validos) / len(tiempos_validos) if tiempos_validos else 0

        intentos_json = []
        for r in self.resultados:
            intentos_json.append({
                "intento": r["intento"],
                "resultado": "exito" if r["exito"] else "fallo",
                "latencia_ms": r["tiempo_ms"] if r["exito"] else 0
            })

        # ----------------------------
        # NUEVO FORMATO JSON
        # ----------------------------
        data = {
            "id_paciente": self.id_paciente,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "modulo": "Motor-DragDrop",
            "metrica_principal": "Tiempo de Reacción",
            "valor_promedio": round(promedio, 2),
            "unidad": "ms",
            "intentos": intentos_json,
            "observaciones_ia": self.generar_observaciones(promedio)
        }

        self.archivo_json = self.guardar_json(data)
        self.archivo_pdf = self.generar_pdf(data)

        print("PDF generado en:", self.archivo_pdf)

        # ----------------------------
        # UI FINAL
        # ----------------------------
        self.canvas.pack_forget()
        self.top.pack_forget()

        frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL, corner_radius=20)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.6)

        ctk.CTkLabel(
            frame,
            text="Juego finalizado",
            font=("Arial", 28, "bold"),
            text_color=COLOR_TEXTO
        ).pack(pady=30)

        ctk.CTkButton(
            frame,
            text="Abrir PDF",
            command=lambda: self.abrir_archivo(self.archivo_pdf),
            height=50
        ).pack(pady=15)

        ctk.CTkButton(
            frame,
            text="Cerrar",
            command=self.destroy,
            fg_color="#EF4444",
            height=50
        ).pack(pady=10)

