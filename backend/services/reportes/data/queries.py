def cargar_devoluciones_detalle(reportes_queries, filtros):
    """
    Ejecuta la query base de devoluciones detalle.
    """
    return reportes_queries.devoluciones_detalle(filtros)


def cargar_asignaciones_activas(reportes_queries, desde, hasta):
    """
    Obtiene asignaciones activas para agrupación por persona.
    """
    return reportes_queries.asignaciones_activas(
        desde=desde,
        hasta=hasta
    )
