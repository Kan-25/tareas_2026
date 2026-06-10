import reflex as rx
import httpx

class State(rx.State):

    size: int = 2

    matrix: list[list[float]] = [
        [0.0, 0.0],
        [0.0, 0.0],
    ]

    vector: list[float] = [0.0, 0.0]

    solution: list[str] = []
    solution_type: str = ""
    steps: list[list[list[str]]] = []
    final_matrix: list[list[str]] = []
    error: str = ""

    def set_size(self, value: str):
        size = int(value)
        self.size = size

        self.matrix = [
            [0.0 for _ in range(size)]
            for _ in range(size)
        ]

        self.vector = [
            0.0 for _ in range(size)
        ]

        self.solution = []
        self.solution_type = ""
        self.steps = []
        self.final_matrix = []
        self.error = ""

    def update_matrix(self, i: int, j: int, value: str):
        matrix = [row[:] for row in self.matrix]
        try:
            matrix[i][j] = float(value)
        except Exception:
            matrix[i][j] = 0.0
        self.matrix = matrix

    def update_vector(self, i: int, value: str):
        vector = self.vector[:]
        try:
            vector[i] = float(value)
        except Exception:
            vector[i] = 0.0
        self.vector = vector

    def solve(self):
        self.error = ""

        try:
            response = httpx.post(
                "http://backend:8000/gauss-jordan",
                json={
                    "matrix": self.matrix,
                    "vector": self.vector,
                },
                timeout=10.0,
            )

            response.raise_for_status()
            data = response.json()

            self.solution = [
                f"{float(x):.2f}"
                for x in data.get("solution", [])
            ]

            self.solution_type = data.get("solution_type", "")

            raw_steps = data.get("steps", [])
            self.steps = [
                [
                    [f"{float(v):.2f}" for v in row]
                    for row in step
                ]
                for step in raw_steps
            ]

            raw_final = data.get("final_matrix", [])
            self.final_matrix = [
                [f"{float(v):.2f}" for v in row]
                for row in raw_final
            ]

        except Exception as e:
            self.solution = []
            self.solution_type = ""
            self.steps = []
            self.final_matrix = []
            self.error = str(e)


def matrix_inputs():
    return rx.box(
        rx.vstack(
            rx.heading("Entrada de Datos", size="7", color="black"),

            # NOTA: Se eliminó el texto "Selecciona el tamaño del sistema"

            rx.select(
                [str(i) for i in range(2, 7)],
                value=State.size.to_string(),
                on_change=State.set_size,
                width="150px",
                color="black", # Forzado a negro sólido
                bg="white",
            ),

            rx.divider(border_color="#cccccc"),

            rx.foreach(
                State.matrix,
                lambda row, i:
                rx.hstack(
                    rx.foreach(
                        row,
                        lambda value, j:
                        rx.input(
                            value=value.to_string(),
                            width="65px",
                            placeholder="0",
                            on_change=lambda v, i=i, j=j: State.update_matrix(i, j, v),
                            color="black", # Forzado a negro sólido
                            bg="#f8f9fa",
                            border_color="#cccccc",
                        ),
                    ),
                    rx.text("=", color="black", font_weight="bold"),
                    rx.input(
                        value=State.vector[i].to_string(),
                        width="65px",
                        on_change=lambda v, i=i: State.update_vector(i, v),
                        color="black", # Forzado a negro sólido
                        bg="#e6f2ff",
                        border_color="#b3d9ff",
                    ),
                    spacing="2",
                ),
            ),

            rx.button(
                "Resolver Sistema",
                on_click=State.solve,
                width="100%",
                size="4",
                color_scheme="blue",
            ),
            spacing="4",
            width="100%",
            align="start",
        ),
        width="fit-content",
        min_width="320px",
        padding="2em",
        bg="white",
        box_shadow="lg",
        border_radius="20px",
        overflow_x="auto",
    )


def solution_status():
    return rx.cond(
        State.solution_type != "",
        rx.box(
            rx.heading(State.solution_type, size="5", color="black"),
            width="100%",
            padding="0.8em",
            bg=rx.cond(
                State.solution_type == "Solución Única",
                "#d4edda", # Verde claro hex
                rx.cond(
                    State.solution_type == "Infinitas Soluciones",
                    "#fff3cd", # Amarillo claro hex
                    "#f8d7da", # Rojo claro hex
                ),
            ),
            border_radius="10px",
        ),
        rx.fragment(),
    )


def solution_view():
    return rx.cond(
        State.solution != [],
        rx.box(
            rx.heading("Valores de las Variables", size="5", color="black", margin_bottom="0.8em"),
            rx.hstack(
                rx.foreach(
                    State.solution,
                    lambda value, i:
                    rx.box(
                        rx.text(f"x{i + 1} = ", font_weight="bold", color="black", as_="span"),
                        rx.text(value, font_size="18px", color="black", font_weight="bold", as_="span"),
                        padding="0.4em 0.8em",
                        bg="#e6f2ff",
                        border="1px solid #b3d9ff",
                        border_radius="8px",
                    ),
                ),
                wrap="wrap",
                spacing="3",
                width="100%",
            ),
            width="100%",
            margin_bottom="1em",
        ),
        rx.fragment(),
    )


def final_matrix_view():
    return rx.cond(
        State.final_matrix != [],
        rx.box(
            rx.heading("Matriz Escalonada Reducida", size="5", color="black", margin_bottom="0.8em"),
            rx.vstack(
                rx.foreach(
                    State.final_matrix,
                    lambda row:
                    rx.hstack(
                        rx.foreach(
                            row,
                            lambda value:
                            rx.box(
                                rx.text(
                                    value,
                                    font_family="monospace",
                                    white_space="nowrap",
                                    color="black", # Forzado a negro sólido
                                    font_size="0.9em"
                                ),
                                border="1px solid #cccccc",
                                padding="0.3em",
                                min_width="55px",
                                text_align="center",
                                border_radius="6px",
                                bg="#f8f9fa",
                            ),
                        ),
                        spacing="1",
                    ),
                ),
                spacing="1",
            ),
            width="100%",
            margin_bottom="1em",
        ),
        rx.fragment(),
    )


def steps_view():
    return rx.cond(
        State.steps != [],
        rx.box(
            rx.heading("Pasos del Método", size="5", color="black", margin_bottom="0.8em"),
            rx.box(
                rx.vstack(
                    rx.foreach(
                        State.steps,
                        lambda step, idx:
                        rx.box(
                            rx.text(f"Paso {idx + 1}", font_weight="bold", color="black", margin_bottom="0.3em", font_size="0.9em"),
                            rx.vstack(
                                rx.foreach(
                                    step,
                                    lambda row:
                                    rx.hstack(
                                        rx.foreach(
                                            row,
                                            lambda value:
                                            rx.box(
                                                rx.text(
                                                    value,
                                                    font_family="monospace",
                                                    white_space="nowrap",
                                                    color="black", # Forzado a negro sólido
                                                    font_size="0.8em"
                                                ),
                                                border="1px solid #cccccc",
                                                padding="0.2em",
                                                min_width="50px",
                                                text_align="center",
                                                border_radius="4px",
                                                bg="white",
                                            ),
                                        ),
                                        spacing="1",
                                    ),
                                ),
                                spacing="1",
                            ),
                            width="100%",
                            bg="#f1f3f5",
                            padding="0.8em",
                            border_radius="8px",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                max_height="350px",
                overflow_y="auto",
                padding_right="0.5em",
                border_radius="8px",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def error_view():
    return rx.cond(
        State.error != "",
        rx.box(
            rx.text(State.error, color="#721c24", font_weight="bold"),
            bg="#f8d7da",
            padding="1em",
            border_radius="10px",
            width="100%",
            margin_top="1em"
        ),
        rx.fragment(),
    )


def index():
    return rx.container(
        rx.vstack(
            rx.heading("Método de Gauss-Jordan", size="9", color="#3b82f6"),
            rx.text(
                "Resolución de sistemas de ecuaciones lineales",
                color="#9ca3af",
                font_size="18px",
            ),
            rx.hstack(
                matrix_inputs(),
                rx.box(
                    rx.vstack(
                        solution_status(),
                        solution_view(),
                        final_matrix_view(),
                        steps_view(),
                        error_view(),
                        spacing="4",
                        width="100%",
                        align="start",
                    ),
                    flex="1", 
                    min_width="350px",
                    padding="2em",
                    bg="white",
                    box_shadow="lg",
                    border_radius="20px",
                ),
                width="100%",
                spacing="6",
                align="start",
                flex_wrap="wrap", 
            ),
            spacing="6",
            width="100%",
        ),
        max_width="1400px",
        padding="2em",
    )

app = rx.App()
app.add_page(index)