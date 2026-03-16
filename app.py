import streamlit as st
import math

# Configuración de la página para móvil
st.set_page_config(page_title="Calculadora Pro", layout="centered")

st.title("🏗️ Calculadora de Construcción")
st.write("Herramienta para presupuestos en terreno.")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏠 Cobertizos", "🚧 Rejas", "🧱 Muros"])

# --- PESTAÑA 1: COBERTIZOS Y TECHOS ---
with tab1:
    st.header("Techumbres y Cobertizos")
    
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
        # Lógica de cálculo
        p_decimal = pendiente / 100
        area_real = (largo * ancho) * math.sqrt(1 + p_decimal**2)
        planchas = math.ceil((area_real * 1.1) / 2.6) # 10% pérdida
        
        # Un pilar cada 2 metros + el inicial
        cant_pilares = math.ceil(largo / 2) + 1
        
        # Vigas y Costaneras (tiras de 6m)
        tiras_viga = math.ceil(largo / 6)
        cant_costaneras = math.ceil(ancho / 0.6) + 1
        tiras_costanera = math.ceil((cant_costaneras * largo) / 6)

        st.success(f"**Resultados para {area_real:.2f} m²**")
        c1, c2 = st.columns(2)
        c1.metric("Planchas Techo", f"{planchas} un")
        c1.metric("Pilares (2.5m)", f"{cant_pilares} un")
        c2.metric("Vigas (6m)", f"{tiras_viga} tiras")
        c2.metric("Costaneras (6m)", f"{tiras_costanera} tiras")
        st.info(f"Material: {medida}")

# --- PESTAÑA 2: REJAS ---
with tab2:
    st.header("Rejas y Portones")
    tipo = st.radio("Tipo:", ["Reja Fija", "Portón Corredera"])
    
    col_r1, col_r2 = st.columns(2)
    ancho_r = col_r1.number_input("Ancho Total (m)", value=3.0)
    alto_r = col_r2.number_input("Alto Total (m)", value=2.0)
    separacion = st.slider("Separación entre barras (cm)", 5, 20, 12)

    if st.button("Calcular Reja"):
        sep_m = separacion / 100
        t_marco = math.ceil(((ancho_r * 2) + (alto_r * 2)) / 6)
        c_barras = math.ceil(ancho_r / sep_m) + 1
        t_int = math.ceil((c_barras * alto_r) / 6)
        
        st.write(f"### Materiales para {tipo}")
        st.write(f"✅ Marco: **{t_marco}** tiras de 6m")
        st.write(f"✅ Interior: **{t_int}** tiras de 6m")
        if tipo == "Portón":
            st.warning("No olvides incluir: Riel, Ruedas y Kit de motor.")

# --- PESTAÑA 3: MUROS ---
with tab3:
    st.header("Albañilería")
    m_largo = st.number_input("Largo del Muro (m)", value=10.0)
    m_alto = st.number_input("Alto del Muro (m)", value=2.0)
    tipo_l = st.selectbox("Ladrillo", ["Fiscal (50 u/m2)", "Princesa (38 u/m2)", "Bloque (12.5 u/m2)"])
    
    if st.button("Calcular Muro"):
        area = m_largo * m_alto
        rend = {"Fiscal (50 u/m2)": 50, "Princesa (38 u/m2)": 38, "Bloque (12.5 u/m2)": 12.5}
        total_ladrillos = math.ceil(area * rend[tipo_l] * 1.05) # 5% perdida
        st.metric("Total Ladrillos", f"{total_ladrillos} un")
        st.write(f"Mezcla estimada: {math.ceil(area * 0.22)} sacos de cemento.")
