def calcular_rejas(alto, ancho, separacion_cm, perfil_marco, perfil_barras, orientacion):
    """
    Calcula los materiales necesarios para construir una reja.
    """
    try:
        # Convertir separación a metros
        separacion = separacion_cm / 100

        # Cálculo del marco
        marco_total = (alto * 2) + (ancho * 2)
        perfiles_marco = 1 if marco_total <= 6.00 else (marco_total // 6)
        sobrante_marco = 6.00 - (marco_total % 6) if marco_total <= 6.00 else 0

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

        # Resultados
        return {
            "perfil_marco": perfil_marco,
            "perfil_barras": perfil_barras,
            "marco_total": marco_total,
            "perfiles_marco": perfiles_marco,
            "sobrante_marco": sobrante_marco,
            "cantidad_barras": cantidad_barras,
            "perfiles_barras": perfiles_barras,
            "sobrante_barras": sobrante_barras,
        }
    except ValueError:
        raise ValueError("Por favor, ingresa valores numéricos válidos.")