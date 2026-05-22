import tkinter as tk
from tkinter import ttk
from calculos.rejas_portones import calcular_rejas  # Importar el cálculo de rejas
from calculos.porton import calcular_porton        # Importar el cálculo de portones

# Función para la ventana de cálculo de Rejas
def ventana_reja():
    nueva_ventana = tk.Toplevel(ventana)
    nueva_ventana.title("Cálculo para Rejas")

    tk.Label(nueva_ventana, text="Introduce las dimensiones:").pack(pady=10)

    tk.Label(nueva_ventana, text="Alto (en metros):").pack()
    entrada_alto = tk.Entry(nueva_ventana)
    entrada_alto.pack()

    tk.Label(nueva_ventana, text="Ancho (en metros):").pack()
    entrada_ancho = tk.Entry(nueva_ventana)
    entrada_ancho.pack()

    tk.Label(nueva_ventana, text="Separación entre barras (en cm):").pack()
    entrada_separacion = tk.Entry(nueva_ventana)
    entrada_separacion.pack()

    tk.Label(nueva_ventana, text="Selecciona el perfil del marco:").pack(pady=5)
    perfiles_marco = ["15mm x 15mm", "20mm x 20mm", "30mm x 30mm", "40mm x 40mm"]
    combo_marco = ttk.Combobox(nueva_ventana, values=perfiles_marco, state="readonly")
    combo_marco.pack()

    tk.Label(nueva_ventana, text="Selecciona el perfil de las barras separadoras:").pack(pady=5)
    perfiles_barras = ["10mm x 10mm", "20mm x 10mm", "30mm x 10mm", "40mm x 20mm"]
    combo_barras = ttk.Combobox(nueva_ventana, values=perfiles_barras, state="readonly")
    combo_barras.pack()

    tk.Label(nueva_ventana, text="Selecciona la orientación de las barras:").pack(pady=5)
    orientaciones = ["Vertical", "Horizontal"]
    combo_orientacion = ttk.Combobox(nueva_ventana, values=orientaciones, state="readonly")
    combo_orientacion.pack()

    def calcular():
        try:
            alto = float(entrada_alto.get())
            ancho = float(entrada_ancho.get())
            separacion_cm = float(entrada_separacion.get())
            perfil_marco = combo_marco.get()
            perfil_barras = combo_barras.get()
            orientacion = combo_orientacion.get()

            if not perfil_marco or not perfil_barras or not orientacion:
                tk.Label(nueva_ventana, text="Por favor, selecciona todos los campos.", fg="red").pack(pady=10)
                return

            resultados = calcular_rejas(alto, ancho, separacion_cm, perfil_marco, perfil_barras, orientacion)

            resultado_texto = (
                f"Perfil del marco: {resultados['perfil_marco']}\n"
                f"Perfil de las barras: {resultados['perfil_barras']}\n"
                f"Longitud del marco: {resultados['marco_total']:.2f} metros\n"
                f"Perfiles para el marco: {resultados['perfiles_marco']} (Sobrante: {resultados['sobrante_marco']:.2f} metros)\n"
                f"Número de barras: {resultados['cantidad_barras']}\n"
                f"Perfiles para las barras: {resultados['perfiles_barras']} (Sobrante: {resultados['sobrante_barras']:.2f} metros)"
            )
            tk.Label(nueva_ventana, text=resultado_texto).pack(pady=10)
        except ValueError:
            tk.Label(nueva_ventana, text="Por favor, ingresa valores válidos.", fg="red").pack(pady=10)

    tk.Button(nueva_ventana, text="Calcular", command=calcular).pack(pady=10)

# Función para la ventana de cálculo de Portones
def ventana_porton():
    nueva_ventana = tk.Toplevel(ventana)
    nueva_ventana.title("Cálculo para Portón")

    tk.Label(nueva_ventana, text="Selecciona el tipo de portón:").pack(pady=10)
    tipos_porton = ["Todo en fierro", "Marco en fierro y forrado con zinc"]
    combo_tipo = ttk.Combobox(nueva_ventana, values=tipos_porton, state="readonly")
    combo_tipo.pack()

    tk.Label(nueva_ventana, text="Introduce las dimensiones:").pack(pady=10)

    tk.Label(nueva_ventana, text="Alto (en metros):").pack()
    entrada_alto = tk.Entry(nueva_ventana)
    entrada_alto.pack()

    tk.Label(nueva_ventana, text="Ancho (en metros):").pack()
    entrada_ancho = tk.Entry(nueva_ventana)
    entrada_ancho.pack()

    tk.Label(nueva_ventana, text="Separación entre barras (en cm, solo para todo en fierro):").pack()
    entrada_separacion = tk.Entry(nueva_ventana)
    entrada_separacion.pack()

    tk.Label(nueva_ventana, text="Selecciona el perfil del marco:").pack(pady=5)
    perfiles_marco = ["15mm x 15mm", "20mm x 20mm", "30mm x 30mm", "40mm x 40mm"]
    combo_marco = ttk.Combobox(nueva_ventana, values=perfiles_marco, state="readonly")
    combo_marco.pack()

    tk.Label(nueva_ventana, text="Selecciona el perfil de las barras separadoras (solo para todo en fierro):").pack(pady=5)
    perfiles_barras = ["10mm x 10mm", "20mm x 10mm", "30mm x 10mm", "40mm x 20mm"]
    combo_barras = ttk.Combobox(nueva_ventana, values=perfiles_barras, state="readonly")
    combo_barras.pack()

    tk.Label(nueva_ventana, text="Selecciona la orientación de las barras (solo para todo en fierro):").pack(pady=5)
    orientaciones = ["Vertical", "Horizontal"]
    combo_orientacion = ttk.Combobox(nueva_ventana, values=orientaciones, state="readonly")
    combo_orientacion.pack()

    def calcular():
        try:
            tipo_porton = combo_tipo.get()
            alto = float(entrada_alto.get())
            ancho = float(entrada_ancho.get())
            perfil_marco = combo_marco.get()

            if not tipo_porton or not perfil_marco:
                tk.Label(nueva_ventana, text="Por favor, selecciona el tipo de portón y el perfil del marco.", fg="red").pack(pady=10)
                return

            if tipo_porton == "Todo en fierro":
                perfil_barras = combo_barras.get()
                orientacion = combo_orientacion.get()
                separacion_cm = float(entrada_separacion.get()) if entrada_separacion.get() else 0

                if not perfil_barras or not orientacion:
                    tk.Label(nueva_ventana, text="Por favor, selecciona todos los campos necesarios.", fg="red").pack(pady=10)
                    return

                resultados = calcular_porton(alto, ancho, separacion_cm, perfil_marco, perfil_barras, orientacion)

                resultado_texto = (
                    f"Perfil del marco: {resultados['perfil_marco']}\n"
                    f"Perfil de las barras: {resultados['perfil_barras']}\n"
                    f"Longitud del marco: {resultados['marco_total']:.2f} metros\n"
                    f"Perfiles para el marco: {resultados['perfiles_marco']} (Sobrante: {resultados['sobrante_marco']:.2f} metros)\n"
                    f"Número de barras: {resultados['cantidad_barras']}\n"
                    f"Perfiles para las barras: {resultados['perfiles_barras']} (Sobrante: {resultados['sobrante_barras']:.2f} metros)"
                )
            elif tipo_porton == "Marco en fierro y forrado con zinc":
                marco_total = (alto * 2) + (ancho * 2)
                area_porton = alto * ancho
                resultado_texto = (
                    f"Marco del portón:\n"
                    f"  - Perfil seleccionado: {perfil_marco}\n"
                    f"  - Longitud total: {marco_total:.2f} metros\n"
                    f"Área de forro en zinc: {area_porton:.2f} m²"
                )

            tk.Label(nueva_ventana, text=resultado_texto).pack(pady=10)
        except ValueError:
            tk.Label(nueva_ventana, text="Por favor, ingresa valores válidos.", fg="red").pack(pady=10)

    # Botón para iniciar el cálculo
    tk.Button(nueva_ventana, text="Calcular", command=calcular).pack(pady=10)

def ventana_techumbre():
    nueva_ventana = tk.Toplevel(ventana)
    nueva_ventana.title("Cálculo para Techumbre")

    # Selección del tipo de techo
    tk.Label(nueva_ventana, text="Selecciona el tipo de techo:").pack(pady=10)
    tipos_techo = ["Tejado plano", "Tejado a un agua", "Tejado a dos aguas", "Tejado a cuatro aguas"]
    combo_techo = ttk.Combobox(nueva_ventana, values=tipos_techo, state="readonly")
    combo_techo.pack()

    # Entradas de dimensiones comunes
    tk.Label(nueva_ventana, text="Ancho del techo (en metros):").pack()
    entrada_ancho = tk.Entry(nueva_ventana)
    entrada_ancho.pack()

    tk.Label(nueva_ventana, text="Largo del techo (en metros):").pack()
    entrada_largo = tk.Entry(nueva_ventana)
    entrada_largo.pack()

    # Campo para inclinación (solo visible para techos inclinados)
    etiqueta_inclinacion = tk.Label(nueva_ventana, text="Inclinación del techo (en grados):")
    entrada_inclinacion = tk.Entry(nueva_ventana)

    def mostrar_inclinacion(event):
        tipo_techo = combo_techo.get()
        if tipo_techo in ["Tejado a un agua", "Tejado a dos aguas", "Tejado a cuatro aguas"]:
            etiqueta_inclinacion.pack()
            entrada_inclinacion.pack()
        else:
            etiqueta_inclinacion.pack_forget()
            entrada_inclinacion.pack_forget()

    combo_techo.bind("<<ComboboxSelected>>", mostrar_inclinacion)

    # Selección de materiales y dimensiones
    tk.Label(nueva_ventana, text="Material para las cerchas:").pack()
    materiales_cercha = ["Fierro", "Madera"]
    combo_cercha = ttk.Combobox(nueva_ventana, values=materiales_cercha, state="readonly")
    combo_cercha.pack()

    tk.Label(nueva_ventana, text="Tipo de planchas:").pack()
    materiales_planchas = ["Zinc", "Policarbonato"]
    combo_planchas = ttk.Combobox(nueva_ventana, values=materiales_planchas, state="readonly")
    combo_planchas.pack()

    tk.Label(nueva_ventana, text="Dimensiones de las planchas (Ancho x Largo en metros):").pack()
    dimensiones_planchas = ["0.80 x 1.00", "0.80 x 2.00", "0.80 x 2.50", "0.80 x 3.00", "0.80 x 3.66"]
    combo_dimensiones = ttk.Combobox(nueva_ventana, values=dimensiones_planchas, state="readonly")
    combo_dimensiones.pack()

    def calcular():
        try:
            # Capturar entradas del usuario
            tipo_techo = combo_techo.get()
            ancho = float(entrada_ancho.get())
            largo = float(entrada_largo.get())
            inclinacion_grados = float(entrada_inclinacion.get()) if entrada_inclinacion.get() else 0
            tipo_cercha = combo_cercha.get()
            tipo_planchas = combo_planchas.get()
            dimensiones = combo_dimensiones.get()

            if not tipo_techo or not tipo_cercha or not tipo_planchas or not dimensiones:
                tk.Label(nueva_ventana, text="Por favor, completa todos los campos.", fg="red").pack(pady=10)
                return

            # Convertir dimensiones de las planchas
            ancho_plancha, largo_plancha = map(float, dimensiones.split(" x "))

            # Llamar al cálculo
            from calculos.techumbre import calcular_techumbre_completa
            resultados = calcular_techumbre_completa(ancho, largo, tipo_cercha, tipo_planchas, (ancho_plancha, largo_plancha))

            resultado_texto = (
                f"Tipo de techo: {tipo_techo}\n"
                f"Tipo de cerchas: {resultados['tipo_cercha']}\n"
                f"Tipo de planchas: {resultados['tipo_planchas']}\n"
                f"Total perfiles (marco + refuerzos): {resultados['perfiles_totales']}\n"
                f"Sobrante de perfiles: {resultados['sobrante_perfiles']:.2f} m\n"
                f"Total de planchas necesarias: {resultados['total_planchas']}"
            )
            tk.Label(nueva_ventana, text=resultado_texto).pack(pady=10)
        except ValueError:
            tk.Label(nueva_ventana, text="Por favor, ingresa valores válidos.", fg="red").pack(pady=10)

    tk.Button(nueva_ventana, text="Calcular", command=calcular).pack(pady=10)

# Ventana principal
ventana = tk.Tk()
ventana.title("Calculadora Modular")
ventana.geometry("400x300")

# Botón para abrir la ventana de cálculo para Rejas
tk.Button(ventana, text="Abrir ventana de cálculo para Rejas", command=ventana_reja).pack(pady=10)

# Botón para abrir la ventana de cálculo para Portones
tk.Button(ventana, text="Abrir ventana de cálculo para Portón", command=ventana_porton).pack(pady=10)

tk.Button(ventana, text="Abrir ventana de cálculo para Techumbre", command=ventana_techumbre).pack(pady=10)

# Iniciar el bucle principal de la ventana
ventana.mainloop()