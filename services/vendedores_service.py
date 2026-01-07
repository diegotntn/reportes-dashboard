from domain.vendedores import Vendedor


class VendedoresService:
    """
    Lógica de negocio para vendedores.

    En este sistema:
    - Un vendedor ES una persona del catálogo 'personal'
    - El vendedor puede estar activo o inactivo
    - El vendedor puede asociarse a devoluciones

    Responsabilidades:
    - Crear vendedores
    - Listar vendedores
    - Validar vendedor activo
    - Resolver vendedor por id o nombre

    NO contiene:
    - UI
    - SQL
    - Tkinter
    """

    def __init__(self, db):
        """
        db: instancia de BaseDB (SQLiteDB o MongoDB)
        """
        self.db = db

    # ───────────────────────── CREAR ─────────────────────────
    def crear(self, nombre):
        """
        Crea un nuevo vendedor (persona activa).
        """
        vendedor = Vendedor(id="tmp", nombre=(nombre or "").strip())
        vendedor.validar_nombre()

        # En este sistema, crear vendedor = crear persona
        return self.db.crear_persona(vendedor.nombre)

    # ───────────────────────── LISTAR ─────────────────────────
    def listar(self, solo_activos=True):
        """
        Devuelve DataFrame de vendedores.
        """
        return self.db.listar_personal(solo_activos=solo_activos)

    # ───────────────────────── VALIDACIÓN ─────────────────────────
    def validar_activo(self, vendedor_id):
        """
        Valida que un vendedor exista y esté activo.
        """
        if not vendedor_id:
            raise ValueError("Vendedor no especificado.")

        df = self.db.listar_personal(solo_activos=False)
        row = df[df["id"] == vendedor_id]

        if row.empty:
            raise ValueError("Vendedor no existe.")

        vendedor = Vendedor(
            id=row.iloc[0]["id"],
            nombre=row.iloc[0]["nombre"],
            activo=bool(row.iloc[0]["activo"]),
        )

        vendedor.validar_activo()
        return True

    # ───────────────────────── OBTENER ─────────────────────────
    def obtener(self, vendedor_id):
        """
        Obtiene un vendedor por id.
        """
        if not vendedor_id:
            return None

        df = self.db.listar_personal(solo_activos=False)
        row = df[df["id"] == vendedor_id]
        return row.iloc[0] if not row.empty else None

    def obtener_por_nombre(self, nombre):
        """
        Busca un vendedor por nombre exacto.
        """
        nombre = (nombre or "").strip().lower()
        if not nombre:
            return None

        df = self.db.listar_personal(solo_activos=False)
        for _, r in df.iterrows():
            if r["nombre"].strip().lower() == nombre:
                return r

        return None

    # ───────────────────────── DESACTIVAR ─────────────────────────
    def desactivar(self, vendedor_id):
        """
        Desactiva un vendedor.
        """
        self.validar_activo(vendedor_id)

        # En este sistema, desactivar vendedor = desactivar persona
        self.db.desactivar_persona(vendedor_id)
