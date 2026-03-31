import customtkinter as ctk
import menu
# Nombres de archivos y clases actualizados
from ingenrehab2 import FittsApp
from DragNDrop import DragDropGame
from test3 import MazeApp

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Integral de Rehabilitación")
        self.geometry("1100x760")
        self.configure(fg_color="#0F172A")

        self.id_paciente = ""
        self.nombre_paciente = ""

        # Iniciamos con el login
        menu.crear_pantalla_login(self)

    def limpiar_ventana(self):
        for widget in self.winfo_children():
            widget.destroy()

    def lanzar_juego(self, clase_juego):
        if clase_juego:
            self.limpiar_ventana()
            # Aquí se crea la instancia del juego pasando 'self' como parent
            instancia_juego = clase_juego(self) 
            instancia_juego.pack(fill="both", expand=True)

    def crear_tarjeta_centrada(self, relwidth=0.6, relheight=0.7):
        frame = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=20)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=relwidth, relheight=relheight)
        return frame

    def crear_boton_principal(self, master, texto, comando, color="#22C55E", hover="#16A34A", width=220):
        return ctk.CTkButton(
            master, text=texto, command=comando,
            fg_color=color, hover_color=hover,
            width=width, height=50, font=("Arial", 18, "bold"), corner_radius=12
        )

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()