def calcular_porton(alto, ancho, separacion_cm, perfil_marco, perfil_barras, orientacion):
    """
    Calcula los materiales necesarios para construir un portón.
    """
    try:
        # Convertir separación a metros
        separacion = separacion_cm / 100

        # Cálculo del marco
        marco_total = (alto * 2) + (ancho * 2)
        if marco_total <= 6.00:
            perfiles_marco = 1  # Solo se necesita un perfil
            sobrante_marco = 6.00 - marco_total
        else:
            perfiles_marco = (marco_total // 6) + (1 if marco_total % 6 > 0 else 0)  # Perfiles completos necesarios
            sobrante_marco = 6.00 - (marco_total % 6) if marco_total % 6 > 0 else 0

        # Cálculo de las barras de separación
        if orientacion == "Vertical":
            cantidad_barras = int(ancho / separacion) + 1
            largo_barras = alto
        elif orientacion == "Horizontal":
            cantidad_barras = int(alto / separacion) + 1
            largo_barras = ancho
        else:
            cantidad_barras, largo_barras = 0, 0  # Sin barras en caso de no aplicarse

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