def calcular_kpis(df):
    dev = df.groupby("devolucion_id")["total_devolucion"].first()

    return {
        "devoluciones": int(dev.count()),
        "importe": float(dev.sum()),
        "promedio": float(dev.mean()) if not dev.empty else 0.0,
    }
