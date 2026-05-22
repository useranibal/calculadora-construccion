import math

def calcular_techumbre_completa(ancho, largo, tipo_cercha, tipo_planchas, dimensiones_planchas):
    """
    Calcula los materiales necesarios para una techumbre plana, considerando el marco y los refuerzos.

    :param ancho: Ancho del techo en metros.
    :param largo: Largo del techo en metros.
    :param tipo_cercha: Tipo de material para las cerchas (ejemplo: Fierro o Madera).
    :param tipo_planchas: Tipo de material para las planchas (ejemplo: Zinc, Policorbonato).
    :param dimensiones_planchas: Dimensiones de cada plancha (ancho, largo) en metros.
    :return: Diccionario con los resultados.
    """
    try:
        # Cálculo del marco (perímetro del techo)
        marco_total = (ancho * 2) + (largo * 2)
        perfiles_marco = math.ceil(marco_total / 6.00)  # Cada perfil mide 6.00 metros
        sobrante_marco = (perfiles_marco * 6.00) - marco_total

        # Cálculo de los refuerzos internos (perfiles transversales)
        perfiles_transversales = math.ceil(ancho / 0.80) - 1  # Colocar cada 80 cm
        largo_refuerzos_transversales = perfiles_transversales * largo

        # Cálculo del refuerzo longitudinal (perfil a lo largo del techo)
        perfil_longitudinal = largo

        # Perfiles totales necesarios (marco + refuerzos)
        total_perfiles_largo = marco_total + largo_refuerzos_transversales + perfil_longitudinal
        perfiles_totales = math.ceil(total_perfiles_largo / 6.00)
        sobrante_perfiles = (perfiles_totales * 6.00) - total_perfiles_largo

        # Cálculo de las planchas de cubierta
        ancho_plancha, largo_plancha = dimensiones_planchas
        cantidad_planchas_ancho = math.ceil(ancho / ancho_plancha)
        cantidad_planchas_largo = math.ceil(largo / largo_plancha)
        total_planchas = cantidad_planchas_ancho * cantidad_planchas_largo

        # Resultados finales
        return {
            "tipo_cercha": tipo_cercha,
            "tipo_planchas": tipo_planchas,
            "marco_total": marco_total,
            "perfiles_marco": perfiles_marco,
            "sobrante_marco": sobrante_marco,
            "refuerzos_transversales": perfiles_transversales,
            "refuerzo_longitudinal": 1,
            "perfiles_totales": perfiles_totales,
            "sobrante_perfiles": sobrante_perfiles,
            "total_planchas": total_planchas
        }
    except ValueError:
        raise ValueError("Por favor, ingresa valores numéricos válidos.")