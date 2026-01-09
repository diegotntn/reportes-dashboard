"""
Test de integración (services reales) para ReportesService – NOVIEMBRE.

OBJETIVO:
- Generar reportes con datos reales (mes con datos confirmados)
- Usar sub-rangos aleatorios dentro de noviembre
- Validar estructura y consistencia (no valores exactos)

NO:
- Modifica BD
- Crea registros
- Usa mocks
"""

import random
from datetime import date, timedelta

from backend.db.factory import get_db
from backend.db.mongo.repos.devoluciones_repo import DevolucionesRepo
from backend.db.mongo.reportes.queries import ReportesQueries
from backend.services.personal_service import PersonalService
from backend.services.reportes.service import ReportesService


# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
ANIO = 2025              # ajusta si noviembre es de otro año
MES = 11                 # noviembre
INTENTOS = 3             # cuántos reportes generar
DIAS_MAX_RANGO = 10      # tamaño máximo de sub-rango


# ─────────────────────────────────────────────
# SETUP SERVICES REALES (BD REAL)
# ─────────────────────────────────────────────
def setup_services():
    print("\n🔌 Inicializando services reales (BD real)...")

    provider = get_db()

    devoluciones_repo = DevolucionesRepo(provider._db)
    reportes_queries = ReportesQueries(devoluciones_repo)
    personal_service = PersonalService(provider)

    service = ReportesService(
        reportes_queries=reportes_queries,
        personal_service=personal_service,
    )

    print("✅ Services inicializados\n")
    return service


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def rango_noviembre_aleatorio():
    """
    Genera un sub-rango aleatorio dentro del mes de noviembre.
    """
    inicio_mes = date(ANIO, MES, 1)
    fin_mes = date(ANIO, MES, 30)

    desde = inicio_mes + timedelta(
        days=random.randint(0, 29)
    )

    hasta = desde + timedelta(
        days=random.randint(1, DIAS_MAX_RANGO)
    )

    return desde, min(hasta, fin_mes)


def validar_resultado_basico(resultado):
    """
    Validaciones suaves de estructura y consistencia.
    """
    assert isinstance(resultado, dict)

    for k in (
        "kpis",
        "resumen",
        "general",
        "por_zona",
        "por_pasillo",
        "por_persona",
        "tabla",
    ):
        assert k in resultado, f"Falta clave '{k}' en resultado"

    resumen = resultado["resumen"]

    assert resumen["importe_total"] >= 0
    assert resumen["piezas_total"] >= 0
    assert resumen["devoluciones_total"] >= 0


# ─────────────────────────────────────────────
# TEST PRINCIPAL
# ─────────────────────────────────────────────
def test_reportes_noviembre(service):
    print("📊 TEST: reportes con rangos aleatorios en NOVIEMBRE (BD real)")

    for i in range(INTENTOS):
        print(f"\n🔁 Iteración {i + 1}/{INTENTOS}")

        desde, hasta = rango_noviembre_aleatorio()
        agrupar = random.choice(["Día", "Semana", "Mes"])

        print(f"Rango: {desde} → {hasta}")
        print(f"Agrupar por: {agrupar}")

        resultado = service.generar(
            desde=desde,
            hasta=hasta,
            agrupar=agrupar,
        )

        validar_resultado_basico(resultado)

        print("Resumen:", resultado["resumen"])
        print("Personas:", list(resultado["por_persona"].keys()))


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("\n========== INICIO TEST REPORTES (NOVIEMBRE | BD REAL) ==========")

    service = setup_services()
    test_reportes_noviembre(service)

    print("\n========== FIN TEST REPORTES ==========\n")


if __name__ == "__main__":
    main()
