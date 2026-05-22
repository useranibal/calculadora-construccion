import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import math
import os

class CalculadoraConstruccion:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Materiales v2.0")
        self.root.geometry("650x900")

        # Configuración de Estilos
        self.style = ttk.Style()
        self.style.configure("TNotebook.Tab", font=("Arial", 10))

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(expand=True, fill="both")

        # Creación de pestañas
        self.tab_rejas = ttk.Frame(self.tabs)
        self.tab_techos = ttk.Frame(self.tabs)
        self.tab_muros = ttk.Frame(self.tabs)
        
        self.tabs.add(self.tab_rejas, text="Rejas y Portones")
        self.tabs.add(self.tab_techos, text="Techumbre / Cobertizo")
        self.tabs.add(self.tab_muros, text="Muros y Levantamiento")

        # Inicializar contenido
        self.setup_tab_rejas()
        self.setup_tab_techos()
        self.setup_tab_muros()

    # --- PESTAÑA: REJAS Y PORTONES ---
    def setup_tab_rejas(self):
        container = ttk.Frame(self.tab_rejas, padding="20")
        container.pack(fill="both")
        
        tk.Label(container, text="Configuración de Estructura Metálica", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.var_tipo_reja = tk.StringVar(value="Reja")
        frame_tipo = ttk.Frame(container)
        frame_tipo.pack(pady=5)
        ttk.Radiobutton(frame_tipo, text="Reja Fija", variable=self.var_tipo_reja, value="Reja", command=self.actualizar_interfaz_reja).pack(side="left", padx=15)
        ttk.Radiobutton(frame_tipo, text="Portón Corredera", variable=self.var_tipo_reja, value="Portón", command=self.actualizar_interfaz_reja).pack(side="left", padx=15)

        self.frame_inputs_reja = ttk.Frame(container)
        self.frame_inputs_reja.pack(pady=10, fill="x")

        self.var_perfiles_dif = tk.BooleanVar(value=False)
        ttk.Checkbutton(container, text="¿Usar perfil diferente para el interior?", variable=self.var_perfiles_dif, command=self.actualizar_interfaz_reja).pack(pady=5)

        self.frame_combos = ttk.Frame(container)
        self.frame_combos.pack(pady=5)
        self.list_perfiles = ["20x10 mm","20x20 mm","20x30 mm","20x40 mm", "30x30 mm", "40x40 mm", "50x50 mm"]
        
        tk.Label(self.frame_combos, text="Perfil Marco:").grid(row=0, column=0, padx=5)
        self.combo_marco = ttk.Combobox(self.frame_combos, values=self.list_perfiles, state="readonly", width=15)
        self.combo_marco.current(2)
        self.combo_marco.grid(row=0, column=1)

        self.lbl_perfil_int = tk.Label(self.frame_combos, text="Perfil Interior:")
        self.combo_interior = ttk.Combobox(self.frame_combos, values=self.list_perfiles, state="readonly", width=15)
        self.combo_interior.current(0)

        self.var_automatico = tk.BooleanVar()
        self.chk_automatico = ttk.Checkbutton(container, text="¿Incluir Kit de Motor?", variable=self.var_automatico)
        
        tk.Button(container, text="Calcular Reja", command=self.ejecutar_calculo_reja, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=15)
        
        self.lbl_res_reja = tk.Label(container, text="", justify="left", font=("Consolas", 10), bg="#f0f0f0", relief="sunken", padx=15, pady=15)
        self.lbl_res_reja.pack(fill="x")
        self.actualizar_interfaz_reja()

    def actualizar_interfaz_reja(self):
        if self.var_perfiles_dif.get():
            self.lbl_perfil_int.grid(row=1, column=0, padx=5, pady=5)
            self.combo_interior.grid(row=1, column=1, pady=5)
        else:
            self.lbl_perfil_int.grid_forget()
            self.combo_interior.grid_forget()

        for widget in self.frame_inputs_reja.winfo_children():
            widget.destroy()

        campos = [("Ancho total (m):", "ent_ancho_r"), ("Alto total (m):", "ent_alto_r"), ("Separación barras (cm):", "ent_sep_r")]
        for i, (txt, attr) in enumerate(campos):
            tk.Label(self.frame_inputs_reja, text=txt).grid(row=i, column=0, sticky="w", pady=2)
            ent = tk.Entry(self.frame_inputs_reja)
            ent.grid(row=i, column=1, pady=2, padx=10)
            setattr(self, attr, ent)

        if self.var_tipo_reja.get() == "Portón":
            self.chk_automatico.pack()
        else:
            self.chk_automatico.pack_forget()

    def ejecutar_calculo_reja(self):
        try:
            ancho = float(self.ent_ancho_r.get())
            alto = float(self.ent_alto_r.get())
            sep = float(self.ent_sep_r.get()) / 100
            
            # Cálculo básico tiras 6m
            t_marco = math.ceil(((ancho * 2) + (alto * 2)) / 6)
            c_barras = math.ceil(ancho / sep) + 1
            t_int = math.ceil((c_barras * alto) / 6)

            res = f"--- RESULTADO {self.var_tipo_reja.get().upper()} ---\n"
            res += f"Marco: {t_marco} tiras ({self.combo_marco.get()})\n"
            p_int = self.combo_interior.get() if self.var_perfiles_dif.get() else self.combo_marco.get()
            res += f"Interior: {t_int} tiras ({p_int})\n"
            
            if self.var_tipo_reja.get() == "Portón":
                res += f"Accesorios: Riel {ancho*2}m, 2 Ruedas, Guía superior"
                if self.var_automatico.get():
                    res += ", Kit Motor + Cremalleras"
            self.lbl_res_reja.config(text=res)
        except:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos en Rejas")

    # --- PESTAÑA: TECHUMBRE Y COBERTIZO ---
    def setup_tab_techos(self):
        container = ttk.Frame(self.tab_techos, padding="20")
        container.pack(fill="both")

        tk.Label(container, text="Cálculo de Techumbres y Cobertizos", font=("Arial", 12, "bold")).pack(pady=5)

        # Combo para imágenes (deben estar en carpeta /img)
        self.dict_imagenes = {"1 Agua": "1 agua.jpg", "2 Aguas (Tipo A)": "2 aguas.png", "4 Aguas": "4 aguas.jpg"}
        self.combo_techo = ttk.Combobox(container, values=list(self.dict_imagenes.keys()), state="readonly")
        self.combo_techo.pack(pady=5)
        self.combo_techo.bind("<<ComboboxSelected>>", self.actualizar_imagen_techo)

        self.lbl_img_techo = tk.Label(container, bg="#dcdcdc", width=400, height=180)
        self.lbl_img_techo.pack(pady=5)

        f_inputs = ttk.Frame(container)
        f_inputs.pack(pady=5)
        tk.Label(f_inputs, text="Largo Cobertizo (m):").grid(row=0, column=0, sticky="w")
        self.ent_largo_t = tk.Entry(f_inputs); self.ent_largo_t.grid(row=0, column=1, pady=2)
        
        tk.Label(f_inputs, text="Ancho / Vuelo (m):").grid(row=1, column=0, sticky="w")
        self.ent_ancho_t = tk.Entry(f_inputs); self.ent_ancho_t.grid(row=1, column=1, pady=2)
        
        tk.Label(f_inputs, text="Pendiente (%):").grid(row=2, column=0, sticky="w")
        self.ent_pen_t = tk.Entry(f_inputs); self.ent_pen_t.insert(0, "20"); self.ent_pen_t.grid(row=2, column=1, pady=2)

        # Estructura de Soporte
        tk.Label(container, text="Estructura de Soporte (Pilares cada 2m)", font=("Arial", 10, "bold")).pack(pady=10)
        
        f_struct = ttk.Frame(container)
        f_struct.pack()

        tk.Label(f_struct, text="Material:").grid(row=0, column=0)
        self.combo_mat_pilar = ttk.Combobox(f_struct, values=["Madera", "Fierro"], state="readonly", width=12)
        self.combo_mat_pilar.bind("<<ComboboxSelected>>", self.actualizar_medidas_pilar)
        self.combo_mat_pilar.grid(row=0, column=1, padx=5)

        tk.Label(f_struct, text="Medida Pilar:").grid(row=1, column=0)
        self.combo_med_pilar = ttk.Combobox(f_struct, state="readonly", width=20)
        self.combo_med_pilar.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(container, text="Calcular Presupuesto Cobertizo", command=self.ejecutar_calculo_techo, 
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(pady=15)
        
        self.lbl_res_techo = tk.Label(container, text="", justify="left", font=("Consolas", 10), 
                                      bg="#f9f9f9", relief="sunken", padx=10, pady=10)
        self.lbl_res_techo.pack(fill="x")

    def actualizar_medidas_pilar(self, event):
        if self.combo_mat_pilar.get() == "Madera":
            self.combo_med_pilar['values'] = ["Pino 4x4\" (Cepillado)", "Pino 5x5\" (Cepillado)", "Pino 6x6\" (Cepillado)", "Polín Impregnado 4\""]
        else:
            self.combo_med_pilar['values'] = ["75x75x2 mm (Pilar)", "100x100x3 mm (Pilar)", "50x50x2 mm (Pilar ligero)"]
        self.combo_med_pilar.current(0)

    def actualizar_imagen_techo(self, event):
        archivo = self.dict_imagenes.get(self.combo_techo.get())
        ruta = os.path.join(os.path.dirname(__file__), "img", archivo)
        try:
            img = Image.open(ruta).resize((400, 180), Image.Resampling.LANCZOS)
            self.foto_techo = ImageTk.PhotoImage(img)
            self.lbl_img_techo.config(image=self.foto_techo, text="")
        except:
            self.lbl_img_techo.config(image='', text="[Imagen referencial no encontrada]")

    def ejecutar_calculo_techo(self):
        try:
            l = float(self.ent_largo_t.get())
            a = float(self.ent_ancho_t.get())
            p_decimal = float(self.ent_pen_t.get()) / 100
            
            # Cubierta (Planchas)
            area_real = (l * a) * math.sqrt(1 + p_decimal**2)
            planchas = math.ceil((area_real * 1.1) / 2.6)

            # Lógica de Pilares (Uno cada 2 metros + 1 al inicio)
            # Se asume una sola fila de pilares (cobertizo adosado).
            cant_pilares = math.ceil(l / 2) + 1
            
            # Vigas Cargadoras (Largo total que sostiene los pilares)
            tiras_viga = math.ceil(l / 6)
            
            # Costaneras (Separadas cada 0.6m para sostener planchas)
            cant_costaneras = math.ceil(a / 0.6) + 1
            tiras_costanera = math.ceil((cant_costaneras * l) / 6)

            res = f"--- DETALLE MATERIALES ---\n"
            res += f"Techo: {area_real:.2f} m² -> {planchas} Planchas\n"
            res += f"---------------------------\n"
            res += f"ESTRUCTURA ({self.combo_mat_pilar.get()}):\n"
            res += f"- Pilares (2.5m alto): {cant_pilares} unidades\n"
            res += f"- Vigas Cargadoras: {tiras_viga} tiras de 6m\n"
            res += f"- Costaneras: {tiras_costanera} tiras de 6m\n"
            res += f"Especificación: {self.combo_med_pilar.get()}"
            
            self.lbl_res_techo.config(text=res)
        except:
            messagebox.showerror("Error", "Complete Largo, Ancho y Material")

    # --- PESTAÑA: MUROS ---
    def setup_tab_muros(self):
        container = ttk.Frame(self.tab_muros, padding="20")
        container.pack(fill="both")
        tk.Label(container, text="Cálculo de Albañilería", font=("Arial", 12, "bold")).pack(pady=10)
        
        f = ttk.Frame(container); f.pack()
        tk.Label(f, text="Largo (m):").grid(row=0, column=0); self.ent_largo_m = tk.Entry(f); self.ent_largo_m.grid(row=0, column=1)
        tk.Label(f, text="Alto (m):").grid(row=1, column=0); self.ent_alto_m = tk.Entry(f); self.ent_alto_m.grid(row=1, column=1)
        
        tk.Label(container, text="Tipo de Ladrillo:").pack(pady=5)
        self.combo_ladrillo = ttk.Combobox(container, values=["Princesa (38 u/m2)", "Fiscal (50 u/m2)", "Bloque (12.5 u/m2)"], state="readonly")
        self.combo_ladrillo.current(1); self.combo_ladrillo.pack()
        
        tk.Button(container, text="Calcular Ladrillos", command=self.ejecutar_calculo_muro, bg="#FF9800", fg="white").pack(pady=15)
        self.lbl_res_muro = tk.Label(container, text="", justify="left", font=("Consolas", 10), bg="#fff3e0", relief="sunken", padx=15, pady=15)
        self.lbl_res_muro.pack(fill="x")

    def ejecutar_calculo_muro(self):
        try:
            area = float(self.ent_largo_m.get()) * float(self.ent_alto_m.get())
            rend = {"Princesa (38 u/m2)": 38, "Fiscal (50 u/m2)": 50, "Bloque (12.5 u/m2)": 12.5}
            unidades = math.ceil(area * rend[self.combo_ladrillo.get()] * 1.05)
            self.lbl_res_muro.config(text=f"Área Muro: {area:.2f} m²\nLadrillos: {unidades} unidades (incl. 5% pérdida)\nSacos Cemento: {math.ceil(area*0.22)}")
        except:
            messagebox.showerror("Error", "Ingrese medidas válidas para el muro")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraConstruccion(root)
    root.mainloop()