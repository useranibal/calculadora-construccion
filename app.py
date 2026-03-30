import streamlit as st
import math
import os

# Configuración de la página
st.set_page_config(page_title="Calculadora de Materiales Pro", layout="centered")

# --- FUNCIÓN PARA CARGAR IMÁGENES SEGURAS ---
def mostrar_imagen(nombre_archivo, subtitulo):
    # Esto busca la carpeta 'img' en el mismo directorio donde está este script
    ruta_base = os.path.dirname(__file__)
    ruta_img = os.path.join(ruta_base, "img", nombre_archivo)
    
    if os.path.exists(ruta_img):
        st.image(ruta_img, caption=subtitulo, use_container_width=True)
    else:
        st.info(f"Archivo no encontrado: {nombre_archivo}. Asegúrate de que esté dentro de la carpeta 'img'.")

st.title("🏗️ Calculadora de Construcción")
st.write("Optimizado para presupuestos rápidos en terreno.")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏠 Cobertizos", "🚧 Rejas", "🧱 Muros"])

# --- PESTAÑA 1: COBERTIZOS ---
with tab1:
    st.header("Techumbres y Cobertizos")
    
    dict_imagenes_techos = {
        "1 Agua": "1 agua.jpg", 
        "2 Aguas (Tipo A)": "2 aguas.png", 
        "4 Aguas": "4 aguas.jpg"
    }
    
    tipo_techo = st.selectbox("Tipo de Geometría", list(dict_imagenes_techos.keys()))
    
    # Mostrar imagen de techo
    mostrar_imagen(dict_imagenes_techos[tipo_techo], f"Estructura: {tipo_techo}")

    col1, col2 = st.columns(2)
    with col1:
        largo = st.number_input("Largo Cobertizo (m)", min_value=0.1, value=5.0, step=0.5)
        pendiente = st.number_input("Pendiente (%)", min_value=0, value=20)
    with col2:
        ancho = st.number_input("Ancho / Vuelo (m)", min_value=0.1, value=3.0, step=0.5)
        material_soporte = st.selectbox("Material de Soporte", ["Madera", "Fierro"])

    if material_soporte == "Madera":
        medida_detalle = st.selectbox("Especificación:", ["Pino 4x4\" (Cepillado)", "Pino 6x6\"", "Polín 4\""])
    else:
        medida_detalle = st.selectbox("Especificación:", ["100x100x3 mm (Pilar)", "75x75x2 mm (Pilar)", "100x50x2 mm (Viga)"])

    if st.button("Calcular Cobertizo"):
        p_decimal = pendiente / 100
        area_real = (largo * ancho) * math.sqrt(1 + p_decimal**2)
        planchas = math.ceil((area_real * 1.1) / 2.6)
        cant_pilares = math.ceil(largo / 2) + 1
        tiras_viga = math.ceil(largo / 6)
        cant_costaneras = math.ceil(ancho / 0.6) + 1
        tiras_costanera = math.ceil((cant_costaneras * largo) / 6)

        st.success(f"**Resumen de Materiales ({area_real:.2f} m²)**")
        res1, res2 = st.columns(2)
        res1.metric("Planchas de Techo", f"{planchas} un")
        res1.metric("Pilares (Estructura)", f"{cant_pilares} un")
        res2.metric("Vigas Cargadoras", f"{tiras_viga} (6m)")
        res2.metric("Costaneras", f"{tiras_costanera} (6m)")

# --- PESTAÑA 2: REJAS Y PORTONES ---
with tab2:
    st.header("Estructuras Metálicas")
    tipo_reja = st.radio("Selecciona tipo:", ["Reja Fija", "Portón Corredera"])
    
    # Lógica de imágenes para rejas
    incluir_casa_perro = st.checkbox("Incluir diseño inferior ('Casa Perro')", value=False)
    
    if incluir_casa_perro:
        mostrar_imagen("reja 2.jpg", "Diseño con protección inferior (Casa Perro)")
    else:
        mostrar_imagen("reja 1.png", "Diseño de reja estándar")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        ancho_r = st.number_input("Ancho Total (m)", value=3.0, step=0.1, key="r_ancho")
    with col_r2:
        alto_r = st.number_input("Alto Total (m)", value=2.0, step=0.1, key="r_alto")
    
    separacion_cm = st.slider("Separación entre barras (cm)", 5, 20, 12)

    altura_puntas = 0.0
    if incluir_casa_perro:
        # CAMBIO: Ahora permite hasta 1.0 metro
        altura_puntas = st.number_input("Altura puntas inferiores (m)", min_value=0.1, max_value=1.0, value=0.3, step=0.05)

    st.markdown("---")
    list_perfiles_metal = ["20x10 mm","20x20 mm","20x30 mm","20x40 mm","20x50 mm", "30x30 mm","40x40 mm", "50x50 mm"]
    
    dif_perfil = st.checkbox("¿Usar perfil distinto para barras interiores?")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        perfil_m = st.selectbox("Perfil Marco:", list_perfiles_metal, index=2)
    if dif_perfil:
        with p_col2:
            perfil_i = st.selectbox("Perfil Barras:", list_perfiles_metal, index=0)
    else:
        perfil_i = perfil_m

    if st.button("Calcular Reja"):
        sep_m = separacion_cm / 100
        tiras_marco = math.ceil(((ancho_r * 2) + (alto_r * 2)) / 6)
        
        cant_barras_largas = math.ceil(ancho_r / sep_m) + 1
        metros_interiores = cant_barras_largas * alto_r

        if incluir_casa_perro:
            # Se asume una punta extra entre cada barra larga
            metros_interiores += (cant_barras_largas * altura_puntas)
        
        tiras_interior = math.ceil(metros_interiores / 6)
        
        st.subheader("Lista de Compra")
        st.write(f"📏 **Marco:** {tiras_marco} tiras de 6m — ({perfil_m})")
        st.write(f"📏 **Barras Interiores:** {tiras_interior} tiras de 6m — ({perfil_i})")
        if incluir_casa_perro:
            st.info(f"Cálculo incluye puntas de {altura_puntas}m de alto.")

# --- PESTAÑA 3: MUROS (Sin cambios) ---
with tab3:
    st.header("Cálculo de Albañilería")
    largo_m = st.number_input("Largo (m)", value=5.0, step=1.0, key="m_largo")
    alto_m = st.number_input("Alto (m)", value=2.0, step=0.1, key="m_alto")
    tipo_ladrillo = st.selectbox("Tipo de Ladrillo:", ["Fiscal (50 u/m2)", "Princesa (38 u/m2)", "Bloque (12.5 u/m2)"])
    
    if st.button("Calcular Muro"):
        superficie = largo_m * alto_m
        tabla = {"Fiscal (50 u/m2)": 50, "Princesa (38 u/m2)": 38, "Bloque (12.5 u/m2)": 12.5}
        total = math.ceil(superficie * tabla[tipo_ladrillo] * 1.05)
        st.metric("Total Ladrillos", f"{total} un")