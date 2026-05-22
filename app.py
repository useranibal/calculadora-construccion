import streamlit as st
import math
import urllib.parse
import io

# === CONFIGURACIÓN E INYECCIÓN DE PWA NATIVA ===
st.set_page_config(page_title="Calculadora de Construcción", layout="wide", page_icon="🏗️")

# Código HTML oculto para registrar el Manifest y el Service Worker en el teléfono
pwa_code = """
<link rel="manifest" href="./manifest.json">
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('./service-worker.js').then(function(registration) {
        console.log('ServiceWorker registrado con éxito: ', registration.scope);
      }, function(err) {
        console.log('Error al registrar el ServiceWorker: ', err);
      });
    });
  }
</script>
"""
# Inyectamos de manera invisible en la app
st.components.v1.html(pwa_code, height=0, width=0)
# ===============================================

# Intentar importar ReportLab para la generación del PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora de Materiales & Cotizador Pro", layout="wide", page_icon="🏗️")

# --- BASE DE DATOS DE PRECIOS INTERNOS (REFERENCIA CHILE 2026) ---
if "precios" not in st.session_state:
    st.session_state.precios = {
        "20x10 mm": 6200, "20x20 mm": 7400, "20x30 mm": 8900, "20x40 mm": 10500, "20x50 mm": 12300,
        "30x30x2 mm (Pilar)": 11800, "40x40x2 mm (Pilar)": 14900, "50x50x2 mm (Pilar)": 18500,
        "60x60x2 mm (Pilar)": 21000, "70x70x2 mm (Pilar)": 23800, "75x75x2 mm (Pilar)": 24900,
        "80x80x2 mm (Pilar)": 28500, "100x100x2 mm (Pilar)": 39500, "100x50x2 mm (Viga)": 21500,
        "Pino 4x4\" (Cepillado)": 14500, "Pino 6x6\"": 32000, "Polín 4\"": 7800,
        "Kilo Electrodo E6011 3/32\"": 5200, "Disco Corte 4 1/2\" (1mm)": 1100,
        "Disco Desbaste 4 1/2\"": 2300, "Anticorrosivo (Galón 3.8L)": 18900,
        "Óleo / Esmalte de terminación (Galón 3.8L)": 24500, "Brocha 3\"": 2500,
        "Pomel de 3\" (un)": 1800, "Cerradura de Sobreponer Poli": 16500,
        "Kit Ruedas y Polines Portón": 35000,
        "Plancha de Techo (Zinc/Policarb standard)": 11500, "Tornillo Techero Autoperforante 2\" (Caja 100 un)": 6800,
        "Fiscal (50 u/m2)": 220, "Princesa (38 u/m2)": 480, "Bloque (12.5 u/m2)": 850,
        "Saco Mortero de Pega Listo (25kg)": 4690, "Saco Hormigón Preparado (25kg)": 4490
    }

# --- FUNCIÓN PARA CARGAR IMÁGENES ---
def mostrar_imagen(nombre_archivo, subtitulo):
    ruta_base = os.path.dirname(__file__)
    ruta_img = os.path.join(ruta_base, "img", nombre_archivo)
    if os.path.exists(ruta_img):
        col_margen_izq, col_imagen, col_margen_der = st.columns([0.25, 0.5, 0.25])
        with col_imagen:
            st.image(ruta_img, caption=subtitulo, use_container_width=True)
    else:
        st.info(f"💡 Visualización: {subtitulo}")

if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "tipo_proyecto" not in st.session_state:
    st.session_state.tipo_proyecto = ""

def agregar_al_presupuesto(lista_materiales, tipo_p):
    st.session_state.carrito = lista_materiales
    st.session_state.tipo_proyecto = tipo_p
    st.toast(f"✅ ¡Materiales cargados al presupuesto!", icon="🛒")

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.title("🏗️ Calculadora de Construcción & Cotizador Inteligente")

col_izq, col_der = st.columns([1.5, 1.5])

with col_izq:
    tab1, tab2, tab3 = st.tabs(["🏠 Cobertizos", "🚧 Rejas y Portones", "🧱 Muros de Albañilería"])

    # PESTAÑA 1: COBERTIZOS
# PESTAÑA 1: COBERTIZOS (REPARADA E INTELIGENTE)
    with tab1:
        st.header("Techumbres y Cobertizos")
        dict_imagenes_techos = {"1 Agua": "1 agua.jpg", "2 Aguas (Tipo A)": "2 aguas.png", "4 Aguas": "4 aguas.jpg"}
        tipo_techo = st.selectbox("Tipo de Geometría", list(dict_imagenes_techos.keys()))
        mostrar_imagen(dict_imagenes_techos[tipo_techo], f"Estructura: {tipo_techo}")
        
        c1, c2 = st.columns(2)
        with c1:
            largo = st.number_input("Largo Cobertizo (m)", min_value=0.1, value=5.0, step=0.5, key="cob_largo")
            pendiente = st.number_input("Pendiente (%)", min_value=0, value=20, key="cob_pend")
            # NUEVO: Selector de cubierta real del mercado
            tipo_cubierta = st.selectbox("Tipo de Cubierta / Techo:", ["Zinc Ondulado (3.66x0.85m)", "Policarbonato Alveolar (2.1x2.9m)", "Teja Asfáltica (Paquete)"])
        with c2:
            ancho = st.number_input("Ancho / Vuelo (m)", min_value=0.1, value=3.0, step=0.5, key="cob_ancho")
            material_soporte = st.selectbox("Material de Soporte Principal", ["Madera", "Fierro"])
            medida_detalle = st.selectbox("Especificación de Pilares:", ["30x30x2 mm (Pilar)", "40x40x2 mm (Pilar)", "75x75x2 mm (Pilar)"] if material_soporte=="Fierro" else ["Pino 4x4\" (Cepillado)", "Pino 6x6\""])
        
        poyos_concreto = st.checkbox("¿Pilares enterrados en concreto?", value=True, key="cob_poyos")

        # Inyectamos los nuevos materiales a la base de datos de precios si no existen
        nuevos_precios_techos = {
            "Zinc Ondulado (3.66x0.85m)": 14500,
            "Policarbonato Alveolar (2.1x2.9m)": 28900,
            "Teja Asfáltica (Paquete 3.1m2)": 24000,
            "Plancha OSB 11mm (Base Teja)": 13500,
            "Pino 2x4\" (Vigas/Tijerales)": 6200,
            "Pino 2x2\" (Costaneras)": 2800
        }
        for k, v in nuevos_precios_techos.items():
            if k not in st.session_state.precios:
                st.session_state.precios[k] = v

        if st.button("📊 Calcular Cobertizo"):
            # 1. Área real con pendiente
            area_real = (largo * ancho) * math.sqrt(1 + (pendiente/100)**2)
            
            # Lista de materiales limpia
            lista_cob = []
            
            # 2. CUBICACIÓN DE TECHUMBRE SEGÚN MERCADO CHILE
            if tipo_cubierta == "Zinc Ondulado (3.66x0.85m)":
                planchas = math.ceil((area_real * 1.15) / 2.5) # 2.5 m2 útiles por plancha
                lista_cob.append({"item": "Zinc Ondulado (3.66x0.85m)", "cant": planchas, "unidad": "un"})
                total_fijaciones = planchas * 6
            elif tipo_cubierta == "Policarbonato Alveolar (2.1x2.9m)":
                planchas = math.ceil((area_real * 1.10) / 5.5) # 5.5 m2 útiles por plancha
                lista_cob.append({"item": "Policarbonato Alveolar (2.1x2.9m)", "cant": planchas, "unidad": "un"})
                total_fijaciones = planchas * 10
            else: # Teja Asfáltica
                paquetes_teja = math.ceil(area_real / 3.1) # 3.1 m2 por paquete
                planchas_osb = math.ceil((area_real * 1.05) / 2.98) # Plancha OSB rinde ~2.98 m2
                lista_cob.append({"item": "Teja Asfáltica (Paquete 3.1m2)", "cant": paquetes_teja, "unidad": "paquetes"})
                lista_cob.append({"item": "Plancha OSB 11mm (Base Teja)", "cant": planchas_osb, "unidad": "un"})
                total_fijaciones = (paquetes_teja * 20) + (planchas_osb * 15) # Clavos de teja + tornillos OSB

            # 3. PILARES VERTICALES
            cant_pilares = (math.ceil(largo / 2.5) + 1) * 2
            if cant_pilares < 4: cant_pilares = 4
            lista_cob.append({"item": medida_detalle, "cant": cant_pilares, "unidad": "un" if material_soporte == "Madera" else "tiras 6m"})

            # 4. ESTRUCTURA / ARMAZÓN SUPERIOR (VIGAS Y COSTANERAS REALS)
            # Vigas principales (paralelas y tijerales): estimación en metros lineales
            ml_vigas = (largo * 2) + (ancho * (math.ceil(largo / 0.8) + 1))
            # Costaneras longitudinales (cada 60cm para recibir el techo)
            ml_costaneras = largo * (math.ceil(ancho / 0.6) + 1)

            if material_soporte == "Madera":
                tiras_vigas = math.ceil(ml_vigas / 3.2)
                tiras_costaneras = math.ceil(ml_costaneras / 3.2)
                lista_cob.append({"item": "Pino 2x4\" (Vigas/Tijerales)", "cant": tiras_vigas, "unidad": "un"})
                lista_cob.append({"item": "Pino 2x2\" (Costaneras)", "cant": tiras_costaneras, "unidad": "un"})
            else:
                tiras_viga_fierro = math.ceil((ml_vigas + ml_costaneras) / 6.0)
                lista_cob.append({"item": "100x50x2 mm (Viga)", "cant": tiras_viga_fierro, "unidad": "tiras 6m"})

            # 5. FIJACIONES Y CONCRETO
            cajas_tornillos = math.ceil(total_fijaciones / 100)
            if cajas_tornillos == 0: cajas_tornillos = 1
            lista_cob.append({"item": "Tornillo Techero Autoperforante 2\" (Caja 100 un)", "cant": cajas_tornillos, "unidad": "cajas"})
                
            if poyos_concreto:
                lista_cob.append({"item": "Saco Hormigón Preparado (25kg)", "cant": cant_pilares * 2, "unidad": "sacos"})
                
            agregar_al_presupuesto(lista_cob, f"Cobertizo {tipo_techo} ({largo}m x {ancho}m) - {tipo_cubierta}")

    # PESTAÑA 2: REJAS Y PORTONES (MODO INTELIGENTE DETECTA PORTÓN O REJA)
    with tab2:
        st.header("Estructuras Metálicas")
        tipo_reja = st.radio("Selecciona tipo de estructura:", ["Reja Fija", "Portón Corredera"])
        incluir_casa_perro = st.checkbox("Incluir diseño inferior corto ('Casa Perro')", value=False)
        mostrar_imagen("reja 2.jpg" if incluir_casa_perro else "reja 1.png", "Visualización del diseño")

        cr1, cr2 = st.columns(2)
        with cr1:
            ancho_total = st.number_input("Ancho Total del Frente (m)", value=4.0, step=0.5, key="r_ancho")
            separacion_cm = st.slider("Separación entre barras (cm)", 5, 20, 8)
        with cr2:
            alto_r = st.number_input("Alto de la Estructura (m)", value=2.0, step=0.1, key="r_alto")
            incluye_puerta = st.checkbox("¿Lleva puerta peatonal incorporada?", value=False)

        altura_puntas = st.number_input("Altura casa perro (m)", value=0.3, step=0.05) if incluir_casa_perro else 0.0

        st.markdown("---")
        list_perfiles_metal = ["20x10 mm","20x20 mm","20x30 mm","20x40 mm","20x50 mm", "30x30 mm","40x40 mm"]
        dif_perfil = st.checkbox("¿Usar perfiles más delgados en barras interiores?", value=True)
        
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            perfil_m = st.selectbox("Perfil del Marco Exterior:", list_perfiles_metal, index=2) # 20x30mm
            perfil_i = st.selectbox("Perfil Barras Interiores:", list_perfiles_metal, index=1) if dif_perfil else perfil_m
        
        with p_col2:
            incluye_pilares_tierra = st.checkbox("¿Incluye pilares de sujeción enterrados a tierra?", value=False)
            
            if incluye_pilares_tierra:
                lista_pilares_nuevos = ["30x30x2 mm (Pilar)", "40x40x2 mm (Pilar)", "50x50x2 mm (Pilar)", "60x60x2 mm (Pilar)", "70x70x2 mm (Pilar)", "75x75x2 mm (Pilar)", "80x80x2 mm (Pilar)", "100x100x2 mm (Pilar)"]
                pilar_sostenedor = st.selectbox("Selecciona Medida del Pilar:", lista_pilares_nuevos, index=1)
                
                if tipo_reja == "Reja Fija":
                    distancia_postes = st.number_input("Distancia máxima por pilar (m):", min_value=1.0, max_value=6.0, value=2.0, step=0.5)
                    cant_paños = math.ceil(ancho_total / distancia_postes)
                    cant_pilares_r = cant_paños + 1
                    ancho_por_paño = ancho_total / cant_paños
                    st.info(f"🚧 Modo Reja: Cierre de {ancho_total}m dividido en **{cant_paños} paños** de {ancho_por_paño:.2f}m c/u. Requiere **{cant_pilares_r} pilares**.")
                else:
                    # Es portón de corredera: Pieza única, requiere solo 2 pilares principales de soporte/tope
                    cant_paños = 1
                    ancho_por_paño = ancho_total
                    cant_pilares_r = 2
                    st.info(f"🛞 Modo Portón: Se cubica como **1 sola estructura continua** de {ancho_total}m. Requiere **2 pilares** de apoyo (guía y recepción).")
            else:
                pilar_sostenedor = None
                cant_paños = 1
                ancho_por_paño = ancho_total
                cant_pilares_r = 0

        if st.button("📊 Calcular Estructura Metálica"):
            # 1. CÁLCULO DE MARCOS (DISTINGUE PAÑOS O PIEZA ÚNICA)
            if tipo_reja == "Reja Fija":
                metros_marco_un_paño = (ancho_por_paño * 2) + (alto_r * 2)
                total_metros_marco = metros_marco_un_paño * cant_paños
            else:
                # Portón lleva doble refuerzo inferior o superior a veces, calculamos contorno simple continuo
                total_metros_marco = (ancho_total * 2) + (alto_r * 2)
                
            tiras_marco = math.ceil(total_metros_marco / 6.0)
            
            # 2. BARRAS INTERIORES
            ancho_paño_cm = ancho_por_paño * 100
            espacio_total_barrote = separacion_cm + 2.0
            barrotes_por_paño = math.ceil(ancho_paño_cm / espacio_total_barrote)
            total_barrotes_largos = barrotes_por_paño * cant_paños
            total_barrotes_cortos = total_barrotes_largos if incluir_casa_perro else 0
            
            cortes_largos_por_tira = math.floor(6.0 / alto_r)
            tiras_interiores_largas = total_barrotes_largos / cortes_largos_por_tira if cortes_largos_por_tira > 0 else total_barrotes_largos * (alto_r / 6.0)
            
            tiras_interiores_cortas = 0
            if incluir_casa_perro and altura_puntas > 0:
                cortes_cortos_por_tira = math.floor(6.0 / altura_puntas)
                tiras_interiores_cortas = total_barrotes_cortos / cortes_cortos_por_tira if cortes_cortos_por_tira > 0 else total_barrotes_cortos * (altura_puntas / 6.0)
                
            tiras_interior = math.ceil((tiras_interiores_largas + tiras_interiores_cortas) * 1.05)
            
            # 3. CONSUMIBLES E INSUMOS
            total_uniones = (total_barrotes_largos * 2) + (total_barrotes_cortos * 2) + (cant_paños * 4)
            kilos_electrodo = math.ceil((total_uniones * 0.015) + 1.0)
            discos_corte = math.ceil((total_barrotes_largos + total_barrotes_cortos + (tiras_marco * 2)) / 8)
            
            metros_lineales_totales = total_metros_marco + (total_barrotes_largos * alto_r) + (total_barrotes_cortos * altura_puntas)
            if incluye_pilares_tierra:
                metros_lineales_totales += (cant_pilares_r * (alto_r + 0.6))
            galones_pintura = math.ceil((metros_lineales_totales * 0.15 * 2) / 30.0)
            
            lista_reja = [
                {"item": perfil_m, "cant": tiras_marco, "unidad": "tiras 6m"},
                {"item": perfil_i, "cant": tiras_interior, "unidad": "tiras 6m"},
                {"item": "Kilo Electrodo E6011 3/32\"", "cant": kilos_electrodo, "unidad": "kg"},
                {"item": "Disco Corte 4 1/2\" (1mm)", "cant": discos_corte, "unidad": "un"},
                {"item": "Disco Desbaste 4 1/2\"", "cant": 1 if tiras_interior < 15 else 2, "unidad": "un"},
                {"item": "Anticorrosivo (Galón 3.8L)", "cant": galones_pintura, "unidad": "galón"},
                {"item": "Óleo / Esmalte de terminación (Galón 3.8L)", "cant": galones_pintura, "unidad": "galón"},
                {"item": "Brocha 3\"", "cant": 1, "unidad": "un"}
            ]
            
            if incluye_pilares_tierra and pilar_sostenedor:
                tiras_pilares = math.ceil((cant_pilares_r * (alto_r + 0.60)) / 6.0)
                lista_reja.append({"item": pilar_sostenedor, "cant": tiras_pilares, "unidad": "tiras 6m"})
                lista_reja.append({"item": "Saco Hormigón Preparado (25kg)", "cant": cant_pilares_r * 2, "unidad": "sacos"})
            
            if incluye_puerta:
                lista_reja.append({"item": "Pomel de 3\" (un)", "cant": 3, "unidad": "un"})
                lista_reja.append({"item": "Cerradura de Sobreponer Poli", "cant": 1, "unidad": "un"})
                
            if tipo_reja == "Portón Corredera":
                lista_reja.append({"item": "Kit Ruedas y Polines Portón", "cant": 1, "unidad": "kit"})
                
            agregar_al_presupuesto(lista_reja, f"{tipo_reja} ({ancho_total}m x {alto_r}m)")

    # PESTAÑA 3: MUROS
# PESTAÑA 3: MUROS (SOLO TEÓRICO BÁSICO)
# PESTAÑA 3: MUROS (ALBAÑILERÍA TRADICIONAL O PREPARADA)
    with tab3:
        st.header("Cálculo de Albañilería")
        largo_m = st.number_input("Largo del Muro (m)", value=5.0, step=1.0)
        alto_m = st.number_input("Alto del Muro (m)", value=2.0, step=0.1)
        tipo_ladrillo = st.selectbox("Tipo de Ladrillo Oficial:", ["Fiscal (50 u/m2)", "Princesa (38 u/m2)", "Bloque (12.5 u/m2)"])
        
        # Nueva opción para elegir el tipo de mezcla
        mezcla_tradicional = st.checkbox("¿Hacer mezcla tradicional? (Cemento y Arena por separado)", value=False)
        
        # Aseguramos que los precios de cemento y arena existan en el diccionario si no estaban
        if "Saco Cemento (25kg)" not in st.session_state.precios:
            st.session_state.precios["Saco Cemento (25kg)"] = 4200
        if "Arena Corriente (m3)" not in st.session_state.precios:
            st.session_state.precios["Arena Corriente (m3)"] = 18500

        if st.button("📊 Calcular Muros"):
            area_muro = largo_m * alto_m
            factor_ladrillo = {"Fiscal (50 u/m2)": 50, "Princesa (38 u/m2)": 38, "Bloque (12.5 u/m2)": 12.5}[tipo_ladrillo]
            
            # Cálculo de ladrillos con 5% de pérdida
            total_ladrillos = math.ceil(area_muro * factor_ladrillo * 1.05)
            
            # Lista base con el ladrillo seleccionado
            lista_muro = [{"item": tipo_ladrillo, "cant": total_ladrillos, "unidad": "un"}]
            
            # Rendimientos base según el tipo de ladrillo
            rendimiento_sacos_listos = {"Fiscal (50 u/m2)": 3.0, "Princesa (38 u/m2)": 2.2, "Bloque (12.5 u/m2)": 1.8}[tipo_ladrillo]
            
            if mezcla_tradicional:
                # Conversión teórica: 1 saco listo (25kg) ≈ 0.16 sacos de cemento (25kg) + 0.013 m3 de arena
                # Para el ladrillo Fiscal (3 sacos/m2) esto rinde: 0.5 sacos cemento y 0.04 m3 de arena por m2
                total_sacos_listos_teoricos = area_muro * rendimiento_sacos_listos
                
                cemento_necesario = math.ceil(total_sacos_listos_teoricos * 0.16)
                arena_necesaria = round(total_sacos_listos_teoricos * 0.013, 2)
                
                # Evitar que la arena quede en 0 si el muro es muy chico
                if arena_necesaria == 0:
                    arena_necesaria = 0.1
                
                lista_muro.append({"item": "Saco Cemento (25kg)", "cant": cemento_necesario, "unidad": "sacos"})
                lista_muro.append({"item": "Arena Corriente (m3)", "cant": arena_necesaria, "unidad": "m3"})
                tipo_msg = "Mezcla In Situ"
            else:
                total_sacos_mortero = math.ceil(area_muro * rendimiento_sacos_listos)
                lista_muro.append({"item": "Saco Mortero de Pega Listo (25kg)", "cant": total_sacos_mortero, "unidad": "sacos"})
                tipo_msg = "Mortero Predosificado"
            
            agregar_al_presupuesto(lista_muro, f"Muro de Albañilería ({largo_m}m x {alto_m}m) - {tipo_msg}")

# PANEL DE COSTOS Y EXPORTACIÓN CORREGIDO
# PANEL DE COSTOS Y EXPORTACIÓN MEJORADO VISUALMENTE
with col_der:
    st.header("💰 Costos e Insumos")
    with st.expander("🛠️ Precios Unitarios"):
        for k in st.session_state.precios.keys():
            st.session_state.precios[k] = st.number_input(f"{k}:", value=int(st.session_state.precios[k]), step=100)

    st.markdown("---")
    st.subheader("🛒 Presupuesto Seleccionado")
    
    if not st.session_state.carrito:
        st.warning("Elige opciones y presiona 'Calcular'.")
    else:
        st.markdown(f"### Proyecto: <span style='color:#1E3D59;'>{st.session_state.tipo_proyecto}</span>", unsafe_allow_html=True)
        
        total_materiales = 0
        tabla_datos = []
        for m in st.session_state.carrito:
            nombre = m["item"]
            cantidad = m["cant"]
            p_unitario = st.session_state.precios.get(nombre, 5000)
            
            # Forzamos a entero para evitar decimales molestos (.0)
            subtotal = int(cantidad * p_unitario)
            total_materiales += subtotal
            
            # Formateo limpio para la tabla
            cant_str = f"{cantidad} {m['unidad']}" if isinstance(cantidad, int) else f"{cantidad:.2f} {m['unidad']}"
            tabla_datos.append({
                "Material": nombre, 
                "Cant.": cant_str, 
                "P. Unit": f"${int(p_unitario):,}", 
                "Subtotal": f"${subtotal:,}"
            })
            
        # Mostrar tabla limpia
        st.table(tabla_datos)
        
        # Cálculos finales
        mano_obra = int(total_materiales * 0.75)
        total_general = total_materiales + mano_obra
        
        # --- DISEÑO DE TARJETA RESUMEN EN CUADRO ---
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 16px; color: #64748B;">Neto Materiales:</span>
                <span style="font-size: 16px; font-weight: bold; color: #334155;">${total_materiales:,}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px dashed #CBD5E1; padding-bottom: 10px;">
                <span style="font-size: 16px; color: #64748B;">Mano de Obra (75%):</span>
                <span style="font-size: 16px; font-weight: bold; color: #334155;">${mano_obra:,}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 20px; font-weight: bold; color: #1E3D59;">TOTAL ESTIMADO:</span>
                <span style="font-size: 24px; font-weight: 900; color: #10B981;">${total_general:,}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        nom_cliente = st.text_input("Cliente:", value="Juan Pérez")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # BOTÓN WHATSAPP
        url_wa = f"https://wa.me/?text={urllib.parse.quote(f'Cotización para {nom_cliente}: {st.session_state.tipo_proyecto} - Total ${total_general:,}')}"
        st.markdown(f'<a href="{url_wa}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:6px; width:100%; font-weight:bold; font-size:16px; cursor:pointer; box-shadow: 0px 4px 6px rgba(0,0,0,0.05);">🟢 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
        
        # GENERACIÓN DE PDF REPARADA
        if REPORTLAB_AVAILABLE:
            def generar_pdf_reportlab():
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                story = []
                styles = getSampleStyleSheet()
                style_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1E3D59'), spaceAfter=15)
                
                story.append(Paragraph("🏗️ COTIZACIÓN FORMAL", style_titulo))
                story.append(Paragraph(f"<b>Proyecto:</b> {st.session_state.tipo_proyecto}", styles['BodyText']))
                story.append(Paragraph(f"<b>Cliente:</b> {nom_cliente}", styles['BodyText']))
                story.append(Spacer(1, 15))
                
                data_tabla_pdf = [["Material / Insumo", "Cantidad", "P. Unitario", "Subtotal"]]
                for m in st.session_state.carrito:
                    n = m["item"]
                    c = m["cant"]
                    pu = st.session_state.precios.get(n, 5000)
                    c_str = f"{c} {m['unidad']}" if isinstance(c, int) else f"{c:.2f} {m['unidad']}"
                    data_tabla_pdf.append([n, c_str, f"${int(pu):,}", f"${int(c*pu):,}"])
                    
                t = Table(data_tabla_pdf, colWidths=[240, 90, 90, 90])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3D59')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                    ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
                    ('FONTSIZE', (0,0), (-1,-1), 9),
                ]))
                story.append(t)
                
                # Resumen al final del PDF
                story.append(Spacer(1, 15))
                story.append(Paragraph(f"<b>Neto Materiales:</b> ${total_materiales:,}", styles['BodyText']))
                story.append(Paragraph(f"<b>Mano de Obra:</b> ${mano_obra:,}", styles['BodyText']))
                story.append(Paragraph(f"<b>TOTAL GENERAL:</b> ${total_general:,}", styles['Heading2']))
                
                doc.build(story)
                buffer.seek(0)
                return buffer.getvalue()
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Descargar Ficha PDF",
                data=generar_pdf_reportlab(),
                file_name=f"Cotizacion_{nom_cliente}.pdf",
                mime="application/pdf",
                use_container_width=True
            )