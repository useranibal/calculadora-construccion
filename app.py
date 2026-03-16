import streamlit as st
import math
import os

# Configuración de la página
st.set_page_config(page_title="Calculadora de Construcción", layout="centered")

st.title("🏗️ Calculadora de Construcción")
st.write("Presupuestos rápidos para terreno.")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏠 Cobertizos", "🚧 Rejas", "🧱 Muros"])

# --- PESTAÑA 1: COBERTIZOS Y TECHOS ---
with tab1:
    st.header("Techumbres y Cobertizos")
    
    # Selección de geometría e imagen
    dict_imagenes = {
        "1 Agua": "1 agua.jpg", 
        "2 Aguas (Tipo A)": "2 aguas.png", 
        "4 Aguas": "4 aguas.jpg"
    }
    
    tipo_techo = st.selectbox("Tipo de Geometría", list(dict_imagenes.keys()))
    
    # Mostrar imagen desde la carpeta img
    ruta_img = os.path.join("img", dict_imagenes[tipo_techo])
    if os.path.exists(ruta_img):
        st.image(ruta_img, caption=f"Referencia: {tipo_techo}", use_container_width=True)
    else:
        st.info("Sube las imágenes a la carpeta /img para ver la referencia visual.")

    col1, col2 = st.columns(2)
    with col1:
        largo = st.number_input("Largo Cobertizo (m)", min_value=0.1, value=5.0, step=0.5)
        pendiente = st.number_input("Pendiente (%)", min_value=0, value=20)
    with col2:
        ancho = st.number_input("Ancho / Vuelo (m)", min_value=0.1, value=3.0, step=0.5)
        material = st.selectbox("Material Estructura", ["Madera", "Fierro"])

    if material == "Madera":
        medida = st.selectbox("Viga/Pilar", ["Pino 4x4\" (Cepillado)", "Pino 6x6\"", "Polín 4\""])
    else:
        medida = st.selectbox("Viga/Pilar", ["100x100x3 mm", "75x75x2 mm", "100x50x2 mm"])

    if st.button("Calcular Cobertizo"):
        p_decimal = pendiente / 100
        area_real = (largo * ancho) * math.sqrt(1 + p_decimal**2)
        planchas = math.ceil((area_real * 1.1) / 2.6)
        
        # Lógica: Un pilar cada 2 metros lineales + 1 inicial
        cant_pilares = math.ceil(largo / 2) + 1
        
        tiras_viga = math.ceil(largo / 6)
        cant_costaneras = math.ceil(ancho / 0.6) + 1
        tiras_costanera = math.ceil((cant_costaneras * largo) / 6)

        st.success(f"**Resultados para {area_real:.2f} m²**")
        c1, c2 = st.columns(2)
        c1.metric("Planchas Techo", f"{planchas} un")
        c1.metric("Pilares (2.5m)", f"{cant_pilares} un")
        c2.metric("Vigas (6m)", f"{tiras_viga} tiras")
        c2.metric("Costaneras (6m)", f"{tiras_costanera} tiras")
        st.info(f"Especificación técnica: {medida}")

# --- PESTAÑA 2: REJAS ---
with tab2:
    st.header("Rejas y Portones")
    tipo = st.radio("Tipo de estructura:", ["Reja Fija", "Portón Corredera"])
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        ancho_r = st.number_input("Ancho Total (m)", value=3.0, key="ancho_reja")
    with col_r2:
        alto_r = st.number_input("Alto Total (m)", value=2.0, key="alto_reja")
    
    separacion = st.slider("Separación entre barras (cm)", 5, 20, 12)

    if st.button("Calcular Reja"):
        sep_m = separacion / 100
        t_marco = math.ceil(((ancho_r * 2) + (alto_r * 2)) / 6)
        c_barras = math.ceil(ancho_r / sep_m) + 1
        t_int = math.ceil((c_barras * alto_r) / 6)
        
        st.subheader(f"Lista de Materiales - {tipo}")
        st.write(f"🔹 **Marco:** {t_marco} tiras de 6m")
        st.write(f"🔹 **Barras interiores:** {t_int} tiras de 6m")
        if tipo == "Portón":
            st.warning("⚠️ Considerar adicional: Riel de piso, ruedas de 90mm y Kit de motorización.")

# --- PESTAÑA 3: MUROS ---
with tab3:
    st.header("Cálculo de Albañilería")
    m_largo = st.number_input("Largo del Muro (m)", value=10.0, key="muro_l")
    m_alto = st.number_input("Alto del Muro (m)", value=2.0, key="muro_a")
    tipo_l = st.selectbox("Tipo de Ladrillo", ["Fiscal (50 u/m2)", "Princesa (38 u/m2)", "Bloque (12.5 u/m2)"])
    
    if st.button("Calcular Muro"):
        area = m_largo * m_alto
        rendimientos = {"Fiscal (50 u/m2)": 50, "Princesa (38 u/m2)": 38, "Bloque (12.5 u/m2)": 12.5}
        total_ladrillos = math.ceil(area * rendimientos[tipo_l] * 1.05)
        
        st.metric("Total Ladrillos (con 5% pérdida)", f"{total_ladrillos} un")
        st.write(f"**Mezcla:** Aproximadamente {math.ceil(area * 0.22)} sacos de cemento.")