import reflex as rx
import httpx
from typing import List, Dict, Any

class State(rx.State):
    # Inputs Falsa Posición
    xi: str = ""
    xd: str = ""
    tol_fp: str = ""
    
    # Inputs Bairstow
    coefs_str: str = ""
    r: str = ""
    s: str = ""
    tol_b: str = ""
    
    # Resultados
    resultado_fp: Dict[str, Any] = {}
    resultado_bairstow: Dict[str, Any] = {}
    
    iteraciones_fp: List[Dict[str, Any]] = []
    iteraciones_bairstow: List[Dict[str, Any]] = []
    
    loading: bool = False
    
    # Setters Manuales (Asegúrate de que coincidan abajo)
    def set_xi_val(self, val: str): self.xi = val
    def set_xd_val(self, val: str): self.xd = val
    def set_tol_fp_val(self, val: str): self.tol_fp = val
    def set_r_val(self, val: str): self.r = val
    def set_s_val(self, val: str): self.s = val
    def set_tol_b_val(self, val: str): self.tol_b = val
    def set_coefs_str(self, val: str): self.coefs_str = val

    # Computed Vars para evitar errores de .get() en el Frontend
    @rx.var
    def fp_resultado_final(self) -> str:
        return str(self.resultado_fp.get("resultado_final", ""))

    @rx.var
    def bairstow_factor_display(self) -> str:
        res = self.resultado_bairstow.get("resultado_final", {})
        return str(res.get("factor", "")) if isinstance(res, dict) else ""
    
    # --- Lógica de Backend ---
    async def calcular_falsa_posicion(self):
        self.loading = True
        url = "http://localhost:8001/falsa-posicion"
        try:
            payload = {"xi": float(self.xi), "xd": float(self.xd), "tol": float(self.tol_fp)}
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    self.resultado_fp = data
                    # Normalizamos para la tabla
                    self.iteraciones_fp = [
                        {"iter": i["iter"], "v_a": i["xi"], "v_b": i["xd"], "err": i["ea"]}
                        for i in data.get("iteraciones", [])
                    ]
        except Exception as e:
            rx.window_alert(f"Error: {str(e)}")
        self.loading = False
        
    async def calcular_bairstow(self):
        self.loading = True
        try:
            lista_coefs = [float(c.strip()) for c in self.coefs_str.split(",") if c.strip()]
            payload = {"coefs": lista_coefs, "r": float(self.r), "s": float(self.s), "tol": float(self.tol_b), "max_iter": 100}
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8001/bairstow", json=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    self.resultado_bairstow = data
                    self.iteraciones_bairstow = [
                        {"iter": i["iter"], "v_a": i["r"], "v_b": i["s"], "err": i["err_r"]}
                        for i in data.get("iteraciones", [])
                    ]
        except Exception as e:
            rx.window_alert(f"Error: {str(e)}")
        self.loading = False

def render_table(data_list: Any):
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Iter"),
                rx.table.column_header_cell("Val A"),
                rx.table.column_header_cell("Val B"),
                rx.table.column_header_cell("Error %"),
            )
        ),
        rx.table.body(
            rx.foreach(
                data_list,
                lambda row: rx.table.row(
                    rx.table.cell(row["iter"].to_string()),
                    rx.table.cell(row["v_a"].to_string()), 
                    rx.table.cell(row["v_b"].to_string()),
                    rx.table.cell(row["err"].to_string()),
                )
            )
        ),
        variant="surface", size="1", margin_top="1em"
    )
    
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Calculadora de Métodos Numéricos", size="8", margin_bottom="1em"),
            
            # Falsa Posición
            rx.card(
                rx.vstack(
                    rx.heading("Método de Falsa Posición", size="5"),
                    rx.hstack(
                        rx.input(placeholder="xi", on_change=State.set_xi_val, value=State.xi),
                        rx.input(placeholder="xd", on_change=State.set_xd_val, value=State.xd),
                        rx.input(placeholder="Tol", on_change=State.set_tol_fp_val, value=State.tol_fp),
                    ),
                    rx.button("Calcular Raíz", on_click=State.calcular_falsa_posicion, loading=State.loading, width="100%"),
                    rx.cond(
                        State.iteraciones_fp,
                        rx.vstack(
                            rx.badge(f"Resultado Final: {State.fp_resultado_final}", color_scheme="green", size="3"),
                            render_table(State.iteraciones_fp),
                            width="100%"
                        )
                    ),
                    width="100%", spacing="3"
                ),
                padding="1.5em", width="100%"
            ),
            
            # Bairstow
            rx.card(
                rx.vstack(
                    rx.heading("Método de Bairstow", size="5"),
                    rx.input(placeholder="Coeficientes: 1, -3, 2", on_change=State.set_coefs_str, value=State.coefs_str),
                    rx.hstack(
                        rx.input(placeholder="r", on_change=State.set_r_val, value=State.r),
                        rx.input(placeholder="s", on_change=State.set_s_val, value=State.s),
                        rx.input(placeholder="Tol", on_change=State.set_tol_b_val, value=State.tol_b),
                    ),
                    rx.button("Calcular Factores", on_click=State.calcular_bairstow, color_scheme="indigo", loading=State.loading, width="100%"),
                    rx.cond(
                        State.iteraciones_bairstow,
                        rx.vstack(
                            rx.badge(f"Factor: {State.bairstow_factor_display}", color_scheme="indigo", size="3"),
                            render_table(State.iteraciones_bairstow),
                            width="100%"
                        )
                    ),
                    width="100%", spacing="3"
                ),
                padding="1.5em", width="100%"
            ),
            spacing="7", padding_y="2em"
        ),
    )

app = rx.App()
app.add_page(index)