# OpenRehab ACV — Sistema Integral de Rehabilitación

Sistema de evaluación neuromotora para pacientes post-ACV, desarrollado en Python con interfaz gráfica de escritorio. Permite registrar, medir y exportar resultados de tres pruebas cognitivo-motoras, generando informes en PDF y JSON de forma automática.

---

## ¿Qué mide el sistema?

### Juego 1 — Ley de Fitts (Puntería)
Evalúa la **velocidad y precisión del movimiento voluntario** del miembro superior. El paciente debe tocar círculos que aparecen en distintas posiciones de la pantalla. Se registra el tiempo de reacción por intento y el Índice de Dificultad (ID) según la fórmula de Fitts. Es un test sensible a déficits motores finos como los que produce el ACV.

### Juego 2 — Arrastre y Soltar (Drag & Drop)
Evalúa la **coordinación y control del movimiento** durante tareas de manipulación. El paciente arrastra un objeto desde su posición inicial hasta un objetivo en pantalla. Se miden tiempo, precisión del soltado y cantidad de intentos exitosos. Permite detectar dificultades de agarre, temblor y coordinación viso-motora.

### Juego 3 — Test de Control Motor (Laberinto)
Evalúa la **estabilidad y suavidad del movimiento** a través de laberintos generados aleatoriamente con dificultad progresiva (fácil → medio → difícil). Se registran colisiones, tiempo de recorrido y porcentaje de trayectoria fuera del laberitno, calculando un **índice de ruido motor estimado**. Indicado para detectar ataxia, dismetría y falta de control motor sostenido.

---

## Población objetivo

Este sistema está dirigido a:
- Pacientes adultos en fase de **rehabilitación post-ACV** (accidente cerebrovascular)
- Personas con déficits motores unilaterales (hemiparesia, hemiplegia)
- Uso supervisado por **kinesiólogos, terapistas ocupacionales o neurólogos**
- Entornos clínicos, de consultorio o domiciliario con computadora

La interfaz fue diseñada con botones grandes, alto contraste visual (fondo oscuro / texto blanco) y lenguaje simple para facilitar su uso por parte de pacientes con posibles dificultades cognitivas leves.

---

## Requisitos del sistema

- Python **3.9 o superior**
- Sistema operativo: Windows, macOS o Linux
---

## Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone https://github.com/ndimen/Ingenieria-en-rehabilitacion.git
cd openrehab-acv

```

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

---

## Uso

1. Al iniciar, ingresar el **nombre** y **DNI** del paciente (solo números, 7 u 8 dígitos).
2. Seleccionar uno de los tres juegos desde el Panel de Rehabilitación.
3. Leer las instrucciones en pantalla y presionar **Comenzar evaluación**.
4. Al finalizar cada prueba, los resultados se guardan automáticamente en la carpeta `results/`.
5. Se puede visualizar el informe PDF directamente desde la pantalla de resultados o abrir la carpeta `results/` manualmente.

### Archivos generados

Todos los archivos se guardan en la carpeta `results/` (se crea automáticamente si no existe):

| Tipo | Nombre ejemplo | Contenido |
|------|----------------|-----------|
| JSON | `fitts_12345678_20240601_143022.json` | Datos crudos por intento |
| PDF  | `informe_fitts_12345678_20240601_143022.pdf` | Informe legible para el profesional |
| JSON | `drag_12345678_143022.json` | Resultados del juego de arrastre |
| PDF  | `drag_12345678_143022.pdf` | Informe del juego de arrastre |
| JSON | `estabilidad_12345678_20240601_143022.json` | Resultados del laberinto |
| PDF  | `informe_estabilidad_12345678_20240601_143022.pdf` | Informe del laberinto |

> **Nota:** Los resultados se guardan al finalizar cada prueba. Si el programa se cierra antes de completarla, los datos del intento en curso no se conservan, pero los intentos anteriores dentro de esa sesión tampoco se pierden mientras no se cierre el test a mitad de camino.

---

## Estructura del proyecto

```
openrehab-acv/
│
├── main.py           # Punto de entrada. Ventana principal y navegación entre juegos
├── menu.py           # Pantalla de login y menú selector de juegos
├── ingenrehab2.py    # Juego 1: Ley de Fitts
├── DragNDrop.py      # Juego 2: Arrastre y Soltar
├── test3.py          # Juego 3: Laberinto de control motor
├── requirements.txt  # Dependencias del proyecto
├── results/          # Carpeta de salida (se crea automáticamente)
└── README.md         # Este archivo
```

---

## Dependencias

Ver `requirements.txt`. Las principales son:

- **customtkinter** — Interfaz gráfica moderna sobre Tkinter
- **reportlab** — Generación de informes en PDF

---


