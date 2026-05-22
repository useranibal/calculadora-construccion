import tkinter as tk
from tkinter import ttk

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Calculadora de Materiales de Construcción")
ventana.geometry("400x300")  # Tamaño de la ventana

# Etiqueta de bienvenida
label_bienvenida = tk.Label(ventana, text="Selecciona el tipo de proyecto", font=("Arial", 14))
label_bienvenida.pack(pady=20)

# Menú desplegable para seleccionar proyecto
opciones = ["Levantamiento de Muralla", "Techumbre", "Rejas y Portones de Fierro"]
combo_proyecto = ttk.Combobox(ventana, values=opciones, state="readonly")
combo_proyecto.pack(pady=10)

# Botón para confirmar selección
def seleccionar_proyecto():
    proyecto_seleccionado = combo_proyecto.get()
    print(f"Proyecto seleccionado: {proyecto_seleccionado}")
    if proyecto_seleccionado == "Rejas y Portones de Fierro":
        # Aquí iremos añadiendo más funciones
        abrir_ventana_rejas_portones()

def ventana_reja():
    nueva_ventana = tk.Toplevel(ventana)
    nueva_ventana.title("Cálculo para Rejas")

    # Etiquetas y campos de entrada
    tk.Label(nueva_ventana, text="Introduce las dimensiones:").pack(pady=10)

    tk.Label(nueva_ventana, text="Alto (en metros):").pack()
    entrada_alto = tk.Entry(nueva_ventana)
    entrada_alto.pack()

    tk.Label(nueva_ventana, text="Ancho (en metros):").pack()
    entrada_ancho = tk.Entry(nueva_ventana)
    entrada_ancho.pack()

    tk.Label(nueva_ventana, text="Separación entre fierros (en centímetros):").pack()
    entrada_separacion = tk.Entry(nueva_ventana)
    entrada_separacion.pack()

    # Menú para seleccionar el perfil del marco
    tk.Label(nueva_ventana, text="Selecciona el perfil del marco (mm x mm):").pack()
    perfiles_cuadrados = ["15mm x 15mm", "20mm x 20mm","20mm x 30mm","30mm x 30mm","20mm x 40mm", "40mm x 40mm",
                          "20mm x 50mm","50mm x 50mm", "75mm x 75mm", "100mm x 100mm", "150mm x 150mm"]
    combo_marco = ttk.Combobox(nueva_ventana, values=perfiles_cuadrados, state="readonly")
    combo_marco.pack()

    # Menú para seleccionar el perfil de las barras de separación
    tk.Label(nueva_ventana, text="Selecciona el perfil de las barras de separación (mm x mm):").pack()
    perfiles_rectangulares = ["20mm x 10mm","30mm x 10mm", "40mm x 10mm","50mm x 10mm",
                              "20mm x 20mm", "30mm x 20mm", "40mm x 20mm", "50mm x 20mm",
                              "30mm x 40mm", "30mm x 50mm"]
    combo_barras = ttk.Combobox(nueva_ventana, values=perfiles_rectangulares, state="readonly")
    combo_barras.pack()

    # Menú para seleccionar orientación de las barras de separación
    tk.Label(nueva_ventana, text="¿Separaciones en vertical u horizontal?").pack()
    orientaciones = ["Vertical", "Horizontal"]
    combo_orientacion = ttk.Combobox(nueva_ventana, values=orientaciones, state="readonly")
    combo_orientacion.pack()

    # Botón para realizar el cálculo
    def calcular_materiales():
        try:
            # Capturar valores
            alto = float(entrada_alto.get())
            ancho = float(entrada_ancho.get())
            separacion_cm = float(entrada_separacion.get())
            perfil_marco = combo_marco.get()
            perfil_barras = combo_barras.get()
            orientacion = combo_orientacion.get()

            if not perfil_marco or not perfil_barras or not orientacion:
                tk.Label(nueva_ventana, text="Por favor, selecciona todos los campos.").pack(pady=10)
                return

            # Convertir separación a metros
            separacion = separacion_cm / 100

            # Cálculo del marco
            marco_total = (alto * 2) + (ancho * 2)
            perfiles_marco = marco_total // 6
            sobrante_marco = marco_total % 6
            if sobrante_marco > 0:
                perfiles_marco += 1

            # Cálculo de las barras de separación
            if orientacion == "Vertical":
                cantidad_barras = int(ancho / separacion) + 1
                largo_barras = alto
            else:  # Horizontal
                cantidad_barras = int(alto / separacion) + 1
                largo_barras = ancho

            total_largo_barras = cantidad_barras * largo_barras
            perfiles_barras = total_largo_barras // 6
            sobrante_barras = total_largo_barras % 6
            if sobrante_barras > 0:
                perfiles_barras += 1

            # Mostrar resultados
            resultado = (
                f"Perfil del marco: {perfil_marco}\n"
                f"Perfil de las barras de separación: {perfil_barras}\n"
                f"Longitud total del marco: {marco_total:.2f} metros\n"
                f"Perfiles necesarios para el marco: {int(perfiles_marco)} (Sobrante: {sobrante_marco:.2f} metros)\n"
                f"Número de barras de separación: {cantidad_barras}\n"
                f"Perfiles necesarios para las barras: {int(perfiles_barras)} (Sobrante: {sobrante_barras:.2f} metros)"
            )
            tk.Label(nueva_ventana, text=resultado).pack(pady=10)
        except ValueError:
            tk.Label(nueva_ventana, text="Por favor, ingresa valores numéricos válidos.").pack(pady=10)

    tk.Button(nueva_ventana, text="Calcular", command=calcular_materiales).pack(pady=10)
def abrir_ventana_rejas_portones():
    nueva_ventana = tk.Toplevel(ventana)
    nueva_ventana.title("Rejas y Portones")
    tk.Label(nueva_ventana, text="¿Qué deseas calcular?").pack(pady=10)
    tk.Button(nueva_ventana, text="Reja", command=ventana_reja).pack(pady=5)  # Ahora conecta con ventana_reja
    tk.Button(nueva_ventana, text="Portón", command=None).pack(pady=5)

btn_seleccionar = tk.Button(ventana, text="Seleccionar", command=seleccionar_proyecto)
btn_seleccionar.pack(pady=10)

# Iniciar el loop principal de la ventana
ventana.mainloop()

