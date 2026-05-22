import streamlit as st
import math
import os
import io
import urllib.parse

# Try to import reportlab for robust, beautiful PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
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
        # Fierros y Estructuras (Por tira de 6m)
        "20x10 mm": 6200, "20x20 mm": 7400, "20x30 mm": 8900, "20x40 mm": 10500,
        "20x50 mm": 12300, "30x30 mm": 11800, "40x40 mm": 14900, "50x50 mm": 18500,
        "100x100x3 mm (Pilar)": 42500, "75x75x2 mm (Pilar)": 24900, "100x50x2 mm (Viga)": 21500,
        # Madera y Soportes Cobertizo
        "Pino 4x4\" (Cepillado)": 14500, "Pino 6x6\"": 32000, "Polín 4\"": 7800,
        # Insumos Metal
        "Kilo Electrodo E6011 3/32\"": 5200, "Disco Corte 4 1/2\" (1mm)": 1100,
        "Disco Desbaste 4 1/2\"": 2300, "Anticorrosivo (Galón 3.8L)": 18900,
        "Óleo / Esmalte de terminación (Galón 3.8L)": 24500, "Brocha 3\"": 2500,
        # Accesorios Puerta/Portón
        "Pomel de 3\" (un)": 1800, "Cerradura de Sobreponer Poli": 16500,
        "Kit Ruedas y Polines Portón": 35000,
        # Techumbres
        "Plancha de Techo (Zinc/Policarb standard)": 11500,
        "Tornillo Techero Autoperforante 2\" (Caja 100 un)": 6800,
        # Albañilería y Obra Gruesa
        "Fiscal (50 u/m2)": 220, "Princesa (38 u/m2)": 480, "Bloque (12.5 u/m2)": 850,
        "Saco Mortero de Pega Listo (25kg)": 4690,
        "Saco Hormigón Preparado (25kg)": 4490
    }

# --- FUNCIÓN PARA CARGAR IMÁGENES CON TAMAÑO OPTIMIZADO ---
def mostrar_imagen(nombre_archivo, subtitulo):
    ruta_base = os.path.dirname(__file__)
    ruta_img = os.path.join(ruta_base, "img", nombre_archivo)
    if os.path.exists(ruta_img):
        # Reducción inteligente usando columnas laterales como márgenes
        col_margen_izq, col_imagen, col_margen_der = st.columns([0.2, 0.6, 0.2])
        with col_imagen:
            st.image(ruta_img, caption=subtitulo, use_container_width=True)
    else:
        st.info(f"💡 Visualización: {subtitulo} (Para ver croquis real, añade '{nombre_archivo}' en carpeta 'img')")

# --- INICIALIZAR CANASTA DE MATERIALES EN SESIÓN ---
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "tipo_proyecto" not in st.session_state:
    st.session_state.tipo_proyecto = ""

def agregar_al_presupuesto(lista_materiales, tipo_p):
    st.session_state.carrito = lista_materiales
    st.session_state.tipo_proyecto = tipo_p
    st.toast(f"✅ ¡Materiales de {tipo_p} cargados al presupuesto!", icon="🛒")

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.title("🏗️ Calculadora de Construcción & Cotizador Inteligente")
st.write("Optimizado para cubicar materiales en terreno, calcular mano de obra e imprimir PDF con costos reales de Chile.")

col_izq, col_der = st.columns([1.6, 1.4])

with col_izq:
    tab1, tab2, tab3 = st.tabs(["🏠 Cobertizos", "🚧 Rejas y Portones", "🧱 Muros de Albañilería"])

    # ----------------------------------------
    # PESTAÑA 1: COBERTIZOS
    # ----------------------------------------
    with tab1:
        st.header("Techumbres y Cobertizos")
        
        dict_imagenes_techos = {
            "1 Agua": "1 agua.jpg", 
            "2 Aguas (Tipo A)": "2 aguas.png", 
            "4 Aguas": "4 aguas.jpg"
        }
        tipo_techo = st.selectbox("Tipo de Geometría", list(dict_imagenes_techos.keys()))
        mostrar_imagen(dict_imagenes_techos[tipo_techo], f"Estructura: {tipo_techo}")

        c1, c2 = st.columns(2)
        with c1:
            largo = st.number_input("Largo Cobertizo (m)", min_value=0.1, value=5.0, step=0.5, key="cob_largo")
            pendiente = st.number_input("Pendiente (%)", min_value=0, value=20, key="cob_pend")
        with c2:
            ancho = st.number_input("Ancho / Vuelo (m)", min_value=0.1, value=3.0, step=0.5, key="cob_ancho")
            material_soporte = st.selectbox("Material de Soporte Principal", ["Madera", "Fierro"])

        if material_soporte == "Madera":
            medida_detalle = st.selectbox("Especificación de Pilares:", ["Pino 4x4\" (Cepillado)", "Pino 6x6\"", "Polín 4\""])
        else:
            medida_detalle = st.selectbox("Especificación de Pilares:", ["100x100x3 mm (Pilar)", "75x75x2 mm (Pilar)", "100x50x2 mm (Viga)"])

        poyos_concreto = st.checkbox("¿Pilares enterrados en concreto/cimiento?", value=True, key="cob_poyos")

        if st.button("📊 Calcular e Inyectar Cobertizo"):
            p_decimal = pendiente / 100
            area_real = (largo * ancho) * math.sqrt(1 + p_decimal**2)
            
            planchas = math.ceil((area_real * 1.1) / 2.6)
            cant_pilares = math.ceil(largo / 2) + 1
            tiras_viga = math.ceil(largo / 6) * 2
            cant_costaneras = math.ceil(ancho / 0.6) + 1
            tiras_costanera = math.ceil((cant_costaneras * largo) / 6)
            
            cajas_tornillos = math.ceil((planchas * 8) / 100)
            
            lista_cob = [
                {"item": "Planchas de Techo (Zinc/Policarb standard)", "cant": planchas, "unidad": "un"},
                {"item": medida_detalle, "cant": cant_pilares, "unidad": "un"},
                {"item": "100x50x2 mm (Viga)" if material_soporte == "Fierro" else "Pino 4x4\" (Cepillado)", "cant": tiras_viga, "unidad": "tiras 6m"},
                {"item": "20x40 mm" if material_soporte == "Fierro" else "Pino 4x4\" (Cepillado)", "cant": tiras_costanera, "unidad": "tiras 6m"},
                {"item": "Tornillo Techero Autoperforante 2\" (Caja 100 un)", "cant": cajas_tornillos, "unidad": "caja"}
            ]
            
            if material_soporte == "Fierro":
                lista_cob.append({"item": "Kilo Electrodo E6011 3/32\"", "cant": 2, "unidad": "kg"})
                lista_cob.append({"item": "Disco Corte 4 1/2\" (1mm)", "cant": 2, "unidad": "un"})
                lista_cob.append({"item": "Anticorrosivo (Galón 3.8L)", "cant": 1, "unidad": "galón"})
            
            if poyos_concreto:
                sacos_hormigon = math.ceil(cant_pilares * 1.5)
                lista_cob.append({"item": "Saco Hormigón Preparado (25kg)", "cant": sacos_hormigon, "unidad": "sacos"})

            agregar_al_presupuesto(lista_cob, f"Cobertizo {tipo_techo} ({largo}x{ancho}m)")

    # ----------------------------------------
    # PESTAÑA 2: REJAS Y PORTONES
    # ----------------------------------------
    with tab2:
        st.header("Estructuras Metálicas")
        tipo_reja = st.radio("Selecciona tipo de estructura:", ["Reja Fija", "Portón Corredera"])
        
        incluir_casa_perro = st.checkbox("Incluir diseño inferior corto ('Casa Perro')", value=False)
        if incluir_casa_perro:
            mostrar_imagen("reja 2.jpg", "Diseño con protección inferior tupida (Casa Perro)")
        else:
            mostrar_imagen("reja 1.png", "Diseño de reja estándar")

        cr1, cr2 = st.columns(2)
        with cr1:
            ancho_r = st.number_input("Ancho Total (m)", value=3.0, step=0.5, key="r_ancho")
            separacion_cm = st.slider("Separación entre barras (cm)", 5, 20, 12)
        with cr2:
            alto_r = st.number_input("Alto Total (m)", value=2.0, step=0.1, key="r_alto")
            incluye_puerta = st.checkbox("¿Lleva puerta peatonal / cerradura incorporada?", value=False)

        altura_puntas = 0.0
        if incluir_casa_perro:
            altura_puntas = st.number_input("Altura de puntas intermedias (m)", min_value=0.1, max_value=1.0, value=0.3, step=0.05)

        st.markdown("---")
        list_perfiles_metal = ["20x10 mm","20x20 mm","20x30 mm","20x40 mm","20x50 mm", "30x30 mm","40x40 mm", "50x50 mm"]
        
        dif_perfil = st.checkbox("¿Usar perfiles más delgados en barras interiores?", value=True)
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            perfil_m = st.selectbox("Perfil del Marco Exterior:", list_perfiles_metal, index=3)
            pilar_sostenedor = st.selectbox("Perfil Pilares de Sujeción a Tierra:", ["75x75x2 mm (Pilar)", "100x100x3 mm (Pilar)"])
        with p_col2:
            if dif_perfil:
                perfil_i = st.selectbox("Perfil Barras Interiores:", list_perfiles_metal, index=1)
            else:
                perfil_i = perfil_m
            cant_pilares_r = st.number_input("Cantidad de pilares a enterrar", min_value=1, value=2, step=1)

        if st.button("📊 Calcular e Inyectar Estructura Metálica"):
            # --- 1. CÁLCULO DEL MARCO ---
            metros_marco = (ancho_r * 2) + (alto_r * 2)
            tiras_marco = math.ceil(metros_marco / 6.0)
            
            # --- 2. CÁLCULO DE BARROTES INTERIORES (CORTES REALES) ---
            ancho_cm = ancho_r * 100
            ancho_perfil_cm = 2.0 
            espacio_total_barrote = separacion_cm + ancho_perfil_cm
            num_barrotes = math.ceil(ancho_cm / espacio_total_barrote)
            
            if incluir_casa_perro:
                num_barrotes_cortos = num_barrotes
            else:
                num_barrotes_cortos = 0

            cortes_largos_por_tira = math.floor(6.0 / alto_r)
            if cortes_largos_por_tira > 0:
                tiras_interiores_largas_netas = num_barrotes / cortes_largos_por_tira
            else:
                tiras_interiores_largas_netas = num_barrotes * (alto_r / 6.0)

            tiras_interiores_cortas_netas = 0
            if incluir_casa_perro and altura_puntas > 0:
                cortes_cortos_por_tira = math.floor(6.0 / altura_puntas)
                if cortes_cortos_por_tira > 0:
                    tiras_interiores_cortas_netas = num_barrotes_cortos / cortes_cortos_por_tira
                else:
                    tiras_interiores_cortas_netas = num_barrotes_cortos * (altura_puntas / 6.0)

            total_tiras_interiores_netas = tiras_interiores_largas_netas + tiras_interiores_cortas_netas
            tiras_interior = math.ceil(total_tiras_interiores_netas * 1.05)

            # --- 3. CÁLCULO DE PILARES ---
            tiras_pilares = math.ceil((cant_pilares_r * (alto_r + 0.5)) / 6.0)
            
            # --- 4. CÁLCULO DE SOLDADURA COMPACTA ---
            total_uniones = (num_barrotes * 2) + (num_barrotes_cortos * 2)
            kilos_soldadura_base = total_uniones * 0.015 
            kilos_electrodo = math.ceil(kilos_soldadura_base + 1.0)
            
            total_barras_a_cortar = num_barrotes + num_barrotes_cortos + (tiras_marco * 2)
            discos_corte = math.ceil(total_barras_a_cortar / 8)  
            discos_desbaste = 1 if tiras_interior < 15 else 2
            
            # --- 5. CÁLCULO REAL DE RENDIMIENTO DE PINTURA ---
            metros_lineales_totales = (num_barrotes * alto_r) + (num_barrotes_cortos * altura_puntas) + metros_marco + (cant_pilares_r * (alto_r + 0.5))
            superficie_real_fierro_m2 = metros_lineales_totales * 0.15
            galones_calculados = (superficie_real_fierro_m2 * 2) / 30.0
            galones_pintura = math.ceil(galones_calculados)
            
            lista_reja = [
                {"item": perfil_m, "cant": tiras_marco, "unidad": "tiras 6m"},
                {"item": perfil_i, "cant": tiras_interior, "unidad": "tiras 6m"},
                {"item": pilar_sostenedor, "cant": tiras_pilares, "unidad": "tiras 6m"},
                {"item": "Kilo Electrodo E6011 3/32\"", "cant": kilos_electrodo, "unidad": "kg"},
                {"item": "Disco Corte 4 1/2\" (1mm)", "cant": discos_corte, "unidad": "un"},
                {"item": "Disco Desbaste 4 1/2\"", "cant": discos_desbaste, "unidad": "un"},
                {"item": "Anticorrosivo (Galón 3.8L)", "cant": galones_pintura, "unidad": "galón"},
                {"item": "Óleo / Esmalte de terminación (Galón 3.8L)", "cant": galones_pintura, "unidad": "galón"},
                {"item": "Brocha 3\"", "cant": 1, "unidad": "un"}
            ]
            
            if incluye_puerta:
                lista_reja.append({"item": "Pomel de 3\" (un)", "cant": 3, "unidad": "un"})
                lista_reja.append({"item": "Cerradura de Sobreponer Poli", "cant": 1, "unidad": "un"})
                
            if tipo_reja == "Portón Corredera":
                lista_reja.append({"item": "Kit Ruedas y Polines Portón", "cant": 1, "unidad": "kit"})
                
            sacos_concreto = cant_pilares_r * 2 
            lista_reja.append({"item": "Saco Hormigón Preparado (25kg)", "cant": sacos_concreto, "unidad": "sacos"})
            
            agregar_al_presupuesto(lista_reja, f"{tipo_reja} ({ancho_r}x{alto_r}m)")

    # ----------------------------------------
    # PESTAÑA 3: MUROS
    # ----------------------------------------
    with tab3:
        st.header("Cálculo de Albañilería")
        largo_m = st.number_input("Largo del Muro (m)", value=5.0, step=1.0, key="m_largo")
        alto_m = st.number_input("Alto del Muro (m)", value=2.0, step=0.1, key="m_alto")
        tipo_ladrillo = st.selectbox("Tipo de Ladrillo Oficial:", ["Fiscal (50 u/m2)", "Princesa (38 u/m2)", "Bloque (12.5 u/m2)"])
        
        st.caption("Nota: El cálculo incluye un 5% extra por pérdidas de material en obra e incorpora mortero listo para facilidad en terreno.")

        if st.button("📊 Calcular e Inyectar Muros"):
            superficie = largo_m * alto_m
            tabla = {"Fiscal (50 u/m2)": 50, "Princesa (38 u/m2)": 38, "Bloque (12.5 u/m2)": 12.5}
            
            total_ladrillos = math.ceil(superficie * tabla[tipo_ladrillo] * 1.05)
            sacos_mortero = math.ceil(superficie * 1.3)
            
            lista_muro = [
                {"item": tipo_ladrillo, "cant": total_ladrillos, "unidad": "un"},
                {"item": "Saco Mortero de Pega Listo (25kg)", "cant": sacos_mortero, "unidad": "sacos"}
            ]
            agregar_al_presupuesto(lista_muro, f"Muro de {tipo_ladrillo} ({superficie:.1f} m²)")


# ==========================================
# PANEL DE COSTOS Y GENERACIÓN DE COTIZACIONES (DERECHA)
# ==========================================
with col_der:
    st.header("💰 Lista de Precios e Insumos")
    
    with st.expander("🛠️ Ver / Modificar Precios Unitarios (CLP)"):
        st.info("Ajusta los costos reales de tu proveedor local. Se usarán para el cálculo total de inmediato.")
        for k in st.session_state.precios.keys():
            st.session_state.precios[k] = st.number_input(f"{k}:", value=int(st.session_state.precios[k]), step=100)

    st.markdown("---")
    st.subheader("🛒 Presupuesto del Proyecto Solicitado")
    
    if not st.session_state.carrito:
        st.warning("Aún no has cubicado ningún ítem. Selecciona una pestaña a la izquierda y presiona 'Calcular e Inyectar'.")
    else:
        st.success(f"**Proyecto Activo:** {st.session_state.tipo_proyecto}")
        
        total_materiales = 0
        tabla_datos = []
        
        for idx, m in enumerate(st.session_state.carrito):
            nombre = m["item"]
            cantidad = m["cant"]
            unidad = m["unidad"]
            p_unitario = st.session_state.precios.get(nombre, 5000)
            subtotal = cantidad * p_unitario
            total_materiales += subtotal
            
            tabla_datos.append({
                "Material": nombre,
                "Cant.": f"{cantidad} {unidad}",
                "P. Unit": f"${p_unitario:,}",
                "Subtotal": f"${subtotal:,}"
            })
            
        st.table(tabla_datos)
        
        mano_obra = int(total_materiales * 0.75)
        total_general = total_materiales + mano_obra
        
        c_mat, c_mo, c_tot = st.columns(3)
        c_mat.metric("Materiales + Insumos", f"${total_materiales:,}")
        c_mo.metric("Mano de Obra (75%)", f"${mano_obra:,}")
        c_tot.metric("TOTAL PRESUPUESTO", f"${total_general:,}")
        
        st.markdown("---")
        st.subheader("📲 Compartir y Exportar")
        
        nom_cliente = st.text_input("Nombre del Cliente:", value="Juan Pérez")
        
        # --- GENERACIÓN DE MENSAJE WHATSAPP ---
        msg_whatsapp = (
            f"⚡ *COTIZACIÓN DE TRABAJO* ⚡\n"
            f"Estimado(a) {nom_cliente},\n"
            f"Presentamos el presupuesto para el proyecto: *{st.session_state.tipo_proyecto}*\n\n"
            f"💵 *Detalle de Costos:*\n"
            f"- Materiales y Elementos Indispensables: ${total_materiales:,}\n"
            f"- Mano de Obra Calificada: ${mano_obra:,}\n"
            f"----------------------------------------\n"
            f"💰 *TOTAL NETO ESTIMADO:* **${total_general:,}**\n\n"
            f"Los materiales consideran todos los perfiles de acero/madera, pernos techeros, anticorrosivo, discos de corte, electrodos y concreto de fundación correspondientes.\n"
            f"Le enviaré el PDF formal con el detalle de cada insumo a continuación. ¡Quedo atento a sus comentarios!"
        )
        
        url_wa = f"https://wa.me/?text={urllib.parse.quote(msg_whatsapp)}"
        st.markdown(f'<a href="{url_wa}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; width:100%; font-weight:bold; cursor:pointer;">🟢 Enviar Resumen de Presupuesto por WhatsApp</button></a>', unsafe_allow_html=True)
        
        st.caption("Nota: Presiona el botón verde para enviar los valores de inmediato. El archivo PDF detallado lo puedes descargar abajo y adjuntarlo en el mismo chat.")

        # --- GENERACIÓN DE ARCHIVO PDF CON REPORTLAB ---
        if REPORTLAB_AVAILABLE:
            def generar_pdf_reportlab():
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                story = []
                
                styles = getSampleStyleSheet()
                
                style_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1E3D59'), spaceAfter=15)
                style_h2 = ParagraphStyle('Sub', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#17B890'), spaceAfter=10)
                style_body = ParagraphStyle('Cuerpo', parent=styles['BodyText'], fontSize=10, spaceAfter=8)
                
                story.append(Paragraph("🏗️ COTIZACIÓN FORMAL DE CONSTRUCCIÓN", style_titulo))
                story.append(Paragraph(f"<b>Proyecto:</b> {st.session_state.tipo_proyecto}", style_body))
                story.append(Paragraph(f"<b>Cliente:</b> {nom_cliente}", style_body))
                story.append(Paragraph("<b>Validez de la oferta:</b> 15 días (Sujeto a variación de stock de proveedores)", style_body))
                story.append(Spacer(1, 15))
                
                story.append(Paragraph("📋 Detalle de Insumos y Materiales Asignados:", style_h2))
                
                data_tabla_pdf = [["Descripción de Material / Insumo", "Cantidad", "P. Unitario", "Subtotal"]]
                for m in st.session_state.carrito:
                    n = m["item"]
                    c = m["cant"]
                    u = m["unidad"]
                    pu = st.session_state.precios.get(n, 5000)
                    sb = c * pu
                    data_tabla_pdf.append([n, f"{c} {u}", f"${pu:,}", f"${sb:,}"])
                    
                t = Table(data_tabla_pdf, colWidths=[240, 90, 90, 90])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3D59')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 10),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F5F7FA'), colors.white]),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                    ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                    ('FONTSIZE', (0,1), (-1,-1), 9),
                ]))
                story.append(t)
                story.append(Spacer(1, 20))
                
                story.append(Paragraph("🧾 Resumen Comercial Final del Proyecto", style_h2))
                resumen_pdf = [
                    ["Total Neto de Materiales e Insumos indispensables:", f"${total_materiales:,}"],
                    ["Mano de Obra Estimada (75% sobre insumos):", f"${mano_obra:,}"],
                    ["VALOR TOTAL PRESUPUESTADO:", f"${total_general:,}"]
                ]
                tr = Table(resumen_pdf, colWidths=[350, 160])
                tr.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,-2), 'Helvetica'),
                    ('FONTNAME', (0,2), (-1,2), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,2), (-1,2), 12),
                    ('TEXTCOLOR', (0,2), (-1,2), colors.HexColor('#145A32')),
                    ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                    ('LINEABOVE', (0,2), (-1,2), 1.5, colors.HexColor('#1E3D59')),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(tr)
                
                story.append(Spacer(1, 35))
                story.append(Paragraph("____________________________________________", style_body))
                story.append(Paragraph("<b>Firma y Timbre del Contratista</b>", style_body))
                story.append(Paragraph("Presupuesto automático generado por Calculadora Pro Terreno.", style_body))
                
                doc.build(story)
                buffer.seek(0)
                return buffer.getvalue()

            pdf_data = generar_pdf_reportlab()
            st.download_button(
                label="📥 Descargar Ficha de Cotización Formal (PDF)",
                data=pdf_data,
                file_name=f"Cotizacion_{nom_cliente.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("Para activar la descarga de PDFs impecables en local, recuerda instalar: `pip install reportlab`")