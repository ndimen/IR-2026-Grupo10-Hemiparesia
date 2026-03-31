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
import menu  # <--- NUEVO: Importamos tu archivo de menú

ANCHO = 1100
ALTO = 760
NUM_INTENTOS = 8

COLOR_FONDO = "#0F172A"
COLOR_PANEL = "#1E293B"
COLOR_TEXTO = "#F8FAFC"
COLOR_ACCION = "#22C55E"
COLOR_ERROR = "#EF4444"
COLOR_OBJ = "#38BDF8"
COLOR_TARGET = "#F97316"

class DragDropGame(ctk.CTkFrame):
    def __init__(self, parent): # <--- Quitamos el id_paciente de aquí
        super().__init__(parent, fg_color="#0F172A")

        self.configure(fg_color=COLOR_FONDO)

        # Variables obligatorias para que el menú funcione
        self.id_paciente = ""
        self.nombre_paciente = ""

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

    def crear_pantalla_inicio(self):
        """Esta es la PORTADA del juego que se ve después del menú"""
        self.limpiar_ventana()
        
        frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL, corner_radius=20)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.7, relheight=0.6)

        ctk.CTkLabel(frame, text="Juego 2: Arrastre y Soltar", font=("Arial", 30, "bold")).pack(pady=20)
        ctk.CTkLabel(frame, text=f"Paciente: {self.nombre_paciente}", font=("Arial", 18)).pack(pady=10)
        
        instrucciones = "Instrucciones: Arrastra el círculo azul hacia el objetivo naranja.\nRepite el proceso 8 veces."
        ctk.CTkLabel(frame, text=instrucciones, font=("Arial", 16), wraplength=500).pack(pady=20)

        # Este botón es el que finalmente llama a la función que YA TENÍAS
        ctk.CTkButton(frame, text="Comenzar Juego", command=self.crear_ui, 
                      fg_color=COLOR_ACCION, hover_color="#16A34A", width=200, height=50).pack(pady=20)
        
        ctk.CTkButton(frame, text="Volver al Menú", command=lambda: menu.crear_pantalla_menu(self), 
                      fg_color="#475569", width=200).pack(pady=10)

    # ----------------------------
    def crear_ui(self):
        self.top = ctk.CTkFrame(self, height=100, fg_color=COLOR_PANEL)
        self.top.pack(fill="x")

        self.label_intento = ctk.CTkLabel(
            self.top,
            text=f"Intento {self.intento}/{NUM_INTENTOS}",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_intento.pack(side="left", padx=20)

        self.label_tiempo = ctk.CTkLabel(
            self.top,
            text="Tiempo: 0 ms",
            font=("Arial", 20, "bold"),
            text_color=COLOR_TEXTO
        )
        self.label_tiempo.pack(side="left", padx=20)

        self.label_instr = ctk.CTkLabel(
            self.top,
            text="Arrastrar bola AZUL → NARANJA",
            font=("Arial", 20, "bold"),
            text_color=COLOR_ACCION
        )
        self.label_instr.pack(side="right", padx=20)

        self.canvas = tk.Canvas(self, bg=COLOR_FONDO, highlightthickness=0)
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

        self.target = self.canvas.create_oval(
            self.target_x-radio,
            self.target_y-radio,
            self.target_x+radio,
            self.target_y+radio,
            fill=COLOR_TARGET
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

        with open(nombre, "w") as f:
            json.dump(data, f, indent=4)

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

        data = {
            "paciente": self.id_paciente,
            "intentos": self.resultados
        }

        self.archivo_json = self.guardar_json(data)
        self.archivo_pdf = self.generar_pdf(data)

        print("PDF generado en:", self.archivo_pdf)

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

