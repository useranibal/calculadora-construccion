import streamlit as st
import math
import os

# Configuración de la página para visualización móvil
st.set_page_config(page_title="Calculadora de Materiales Pro", layout="centered")

st.title("🏗️ Calculadora de Construcción")
st.write("Optimizado para presupuestos rápidos en terreno.")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏠 Cobertizos", "🚧 Rejas", "🧱 Muros"])

# --- PESTAÑA 1: COBERTIZOS Y TECHOS ---
with tab1:
    st.header("Techumbres y Cobertizos")
    
    # 1. Selección de Geometría
    dict_imagenes = {
        "1 Agua": "1 agua.jpg", 
        "2 Aguas (Tipo A)": "2 aguas.png", 
        "4 Aguas": "4 aguas.jpg"
    }
    
    tipo_techo = st.selectbox("Tipo de Geometría", list(dict_imagenes.keys()))
    
    # 2. Carga de Imagen Referencial
    ruta_img = os.path.join("img", dict_imagenes[tipo_techo])
    if os.path.exists(ruta_img):
        st.image(ruta_img, caption=f"Estructura: {tipo_techo}", use_container_width=True)
    else:
        st.info("Asegúrate de tener la carpeta 'img' en GitHub con las fotos para ver la referencia.")

    # 3. Entradas de Medidas
    col1, col2 = st.columns(2)
    with col1:
        largo = st.number_input("Largo Cobertizo (m)", min_value=0.1, value=5.0, step=0.5)
        pendiente = st.number_input("Pendiente (%)", min_value=0, value=20)
    with col2:
        ancho = st.number_input("Ancho / Vuelo (m)", min_value=0.1, value=3.0, step=0.5)
        material_soporte = st.selectbox("Material de Soporte", ["Madera", "Fierro"])

    # 4. Selección de Medidas Técnicas
    if material_soporte == "Madera":
        medida_detalle = st.selectbox("Especificación:", ["Pino 4x4\" (Cepillado)", "Pino 6x6\"", "Polín 4\""])
    else:
        medida_detalle = st.selectbox("Especificación:", ["100x100x3 mm (Pilar)", "75x75x2 mm (Pilar)", "100x50x2 mm (Viga)"])

    if st.button("Calcular Cobertizo"):
        # Cálculos de Techumbre
        p_decimal = pendiente / 100
        area_real = (largo * ancho) * math.sqrt(1 + p_decimal**2)
        planchas = math.ceil((area_real * 1.1) / 2.6) # Incluye 10% de pérdida/traslape
        
        # CÁLCULO DE PILARES: Un pilar cada 2 metros lineales + 1 inicial
        cant_pilares = math.ceil(largo / 2) + 1
        
        # Vigas y Costaneras (Cálculo en tiras de 6m)
        tiras_viga = math.ceil(largo / 6)
        cant_costaneras = math.ceil(ancho / 0.6) + 1 # Una costanera cada 60cm
        tiras_costanera = math.ceil((cant_costaneras * largo) / 6)

        st.success(f"**Resumen de Materiales ({area_real:.2f} m²)**")
        res1, res2 = st.columns(2)
        res1.metric("Planchas de Techo", f"{planchas} un")
        res1.metric("Pilares (Estructura)", f"{cant_pilares} un")
        res2.metric("Vigas Cargadoras", f"{tiras_viga} (6m)")
        res2.metric("Costaneras", f"{tiras_costanera} (6m)")
        st.caption(f"Detalle seleccionado: {medida_detalle}")

# --- PESTAÑA 2: REJAS Y PORTONES ---
with tab2:
    st.header("Estructuras Metálicas")
    tipo_reja = st.radio("Selecciona tipo:", ["Reja Fija", "Portón Corredera"])
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        ancho_r = st.number_input("Ancho Total (m)", value=3.0, step=0.1, key="r_ancho")
    with col_r2:
        alto_r = st.number_input("Alto Total (m)", value=2.0, step=0.1, key="r_alto")
    
    separacion_cm = st.slider("Separación entre barras (cm)", 5, 20, 12)
    
    st.markdown("---")
    # Lógica de perfiles personalizables
    list_perfiles_metal = ["20x20 mm", "30x30 mm", "40x40 mm", "50x50 mm", "40x20 mm (Rect)"]
    
    dif_perfil = st.checkbox("¿Deseas usar un perfil distinto para el interior?")
    
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
        # Marco (perímetro)
        tiras_marco = math.ceil(((ancho_r * 2) + (alto_r * 2)) / 6)
        # Barras interiores
        cant_barras = math.ceil(ancho_r / sep_m) + 1
        tiras_interior = math.ceil((cant_barras * alto_r) / 6)
        
        st.subheader("Lista de Compra")
        st.write(f"📏 **Marco:** {tiras_marco} tiras de 6m — ({perfil_m})")
        st.write(f"📏 **Interior:** {tiras_interior} tiras de 6m — ({perfil_i})")
        
        if tipo_reja == "Portón":
            st.info("💡 **Accesorios sugeridos:** Riel de 6m, 2 ruedas con rodamiento y kit de motor.")

# --- PESTAÑA 3: MUROS ---
with tab3:
    st.header("Cálculo de Albañilería")
    
    m_col1, m_col2 = st.columns(2)
    largo_m = m_col1.number_input("Largo (m)", value=5.0, step=1.0)
    alto_m = m_col2.number_input("Alto (m)", value=2.0, step=0.1)
    
    tipo_ladrillo = st.selectbox("Tipo de Ladrillo:", ["Fiscal (50 u/m2)", "Princesa (38 u/m2)", "Bloque (12.5 u/m2)"])
    
    if st.button("Calcular Muro"):
        superficie = largo_m * alto_m
        tabla_rendimiento = {"Fiscal (50 u/m2)": 50, "Princesa (38 u/m2)": 38, "Bloque (12.5 u/m2)": 12.5}
        
        total_unidades = math.ceil(superficie * tabla_rendimiento[tipo_ladrillo] * 1.05) # 5% margen de error
        cemento_est = math.ceil(superficie * 0.22) # Estimación de sacos
        
        st.metric("Total Ladrillos", f"{total_unidades} un")
        st.write(f"Se estima el uso de **{cemento_est} sacos de cemento** para esta superficie.")