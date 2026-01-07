"""
Funciones de agregación para reportes.

Estas funciones:
- NO consultan DB
- NO conocen la UI
- SOLO trabajan con el DataFrame normalizado

Contrato del DataFrame de entrada:
- periodo
- importe
- piezas
- devoluciones
- zona
- pasillo
- persona (si aplica)
"""

# ─────────────────────────────
def agrupa_general(df, kpis):
    """
    Agrupación general por periodo (vista General).

    Retorna:
    {
        "df": DataFrame,
        "x": "periodo",
        "importe_col": str | None,
        "piezas_col": str | None,
        "devoluciones_col": str | None
    }
    """
    if df is None or df.empty:
        return None

    agg = {}
    meta = {
        "df": None,
        "x": "periodo",
        "importe_col": None,
        "piezas_col": None,
        "devoluciones_col": None,
    }

    if kpis.get("importe"):
        agg["importe"] = ("importe", "sum")
        meta["importe_col"] = "importe"

    if kpis.get("piezas"):
        agg["piezas"] = ("piezas", "sum")
        meta["piezas_col"] = "piezas"

    if kpis.get("devoluciones"):
        agg["devoluciones"] = ("devoluciones", "sum")
        meta["devoluciones_col"] = "devoluciones"

    if not agg:
        return None

    df_agg = (
        df.groupby("periodo", as_index=False)
        .agg(**agg)
        .sort_values("periodo")
    )

    meta["df"] = df_agg
    return meta


# ─────────────────────────────
def agrupa_por_zona(df, kpis):
    """
    Agrupación por zona (vista Zonas).

    Retorna:
    {
        "Z11": {
            "df": DataFrame,
            "importe_col": str | None,
            "piezas_col": str | None,
            "devoluciones_col": str | None,
            "resumen": {...}
        },
        ...
    }
    """
    if df is None or df.empty or "zona" not in df.columns:
        return {}

    resultado = {}

    for zona, g in df.groupby("zona"):
        agg = {}
        meta = {
            "df": None,
            "importe_col": None,
            "piezas_col": None,
            "devoluciones_col": None,
            "resumen": {},
        }

        if kpis.get("importe"):
            agg["importe"] = ("importe", "sum")
            meta["importe_col"] = "importe"
            meta["resumen"]["importe"] = float(g["importe"].sum())

        if kpis.get("piezas"):
            agg["piezas"] = ("piezas", "sum")
            meta["piezas_col"] = "piezas"
            meta["resumen"]["piezas"] = int(g["piezas"].sum())

        if kpis.get("devoluciones"):
            agg["devoluciones"] = ("devoluciones", "sum")
            meta["devoluciones_col"] = "devoluciones"
            meta["resumen"]["devoluciones"] = int(g["devoluciones"].sum())

        if not agg:
            continue

        df_agg = (
            g.groupby("periodo", as_index=False)
            .agg(**agg)
            .sort_values("periodo")
        )

        meta["df"] = df_agg
        resultado[zona] = meta

    return resultado


# ─────────────────────────────
def agrupa_por_pasillo(df, kpis):
    """
    Agrupación por pasillo (vista Pasillos).

    Retorna:
    {
        "P1": {
            "df": DataFrame,
            "importe_col": str | None,
            "piezas_col": str | None,
            "devoluciones_col": str | None,
            "resumen": {...}
        },
        ...
    }
    """
    if df is None or df.empty or "pasillo" not in df.columns:
        return {}

    resultado = {}

    for pasillo, g in df.groupby("pasillo"):
        agg = {}
        meta = {
            "df": None,
            "importe_col": None,
            "piezas_col": None,
            "devoluciones_col": None,
            "resumen": {},
        }

        if kpis.get("importe"):
            agg["importe"] = ("importe", "sum")
            meta["importe_col"] = "importe"
            meta["resumen"]["importe"] = float(g["importe"].sum())

        if kpis.get("piezas"):
            agg["piezas"] = ("piezas", "sum")
            meta["piezas_col"] = "piezas"
            meta["resumen"]["piezas"] = int(g["piezas"].sum())

        if kpis.get("devoluciones"):
            agg["devoluciones"] = ("devoluciones", "sum")
            meta["devoluciones_col"] = "devoluciones"
            meta["resumen"]["devoluciones"] = int(g["devoluciones"].sum())

        if not agg:
            continue

        df_agg = (
            g.groupby("periodo", as_index=False)
            .agg(**agg)
            .sort_values("periodo")
        )

        meta["df"] = df_agg
        resultado[pasillo] = meta

    return resultado


# ─────────────────────────────
def tabla_final(df):
    """
    Tabla de detalle final.

    Agrupa por periodo, zona y pasillo si existen.
    """
    if df is None or df.empty:
        return []

    group_cols = ["periodo"]

    if "zona" in df.columns:
        group_cols.append("zona")

    if "pasillo" in df.columns:
        group_cols.append("pasillo")

    grp = (
        df.groupby(group_cols, as_index=False)
        .agg(
            devoluciones=("devoluciones", "sum"),
            piezas=("piezas", "sum"),
            importe=("importe", "sum"),
        )
        .sort_values(group_cols)
    )

    salida = []
    for _, r in grp.iterrows():
        row = {
            "periodo": str(r["periodo"]),
            "devoluciones": int(r["devoluciones"]),
            "piezas": int(r["piezas"]),
            "importe": float(r["importe"]),
        }

        if "zona" in r:
            row["zona"] = r["zona"]

        if "pasillo" in r:
            row["pasillo"] = r["pasillo"]

        salida.append(row)

    return salida
