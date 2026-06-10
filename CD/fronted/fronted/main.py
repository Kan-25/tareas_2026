import reflex as rx
import httpx


class State(rx.State):

    size: int = 2

    matrix: list[list[float]] = [
        [0.0, 0.0],
        [0.0, 0.0]
    ]

    vector: list[float] = [0.0, 0.0]

    result: dict = {}

    def set_size(self, value):

        self.size = int(value)

        self.matrix = [
            [0.0 for _ in range(self.size)]
            for _ in range(self.size)
        ]

        self.vector = [
            0.0 for _ in range(self.size)
        ]

    def update_matrix(self, i, j, value):

        matrix = [row[:] for row in self.matrix]

        try:
            matrix[i][j] = float(value)
        except:
            matrix[i][j] = 0.0

        self.matrix = matrix

    def update_vector(self, i, value):

        vector = self.vector[:]

        try:
            vector[i] = float(value)
        except:
            vector[i] = 0.0

        self.vector = vector

    def solve(self):

        response = httpx.post(
            "http://127.0.0.1:8000/gauss-jordan",
            json={
                "matrix": self.matrix,
                "vector": self.vector
            }
        )

        self.result = response.json()


def matrix_inputs():

    return rx.vstack(

        rx.foreach(

            State.matrix,

            lambda row, i:

            rx.hstack(

                rx.foreach(

                    row,

                    lambda value, j:

                    rx.input(
                        value=str(value),

                        width="60px",

                        on_change=lambda v, i=i, j=j:
                        State.update_matrix(i, j, v)
                    )
                ),

                rx.text("|"),

                rx.input(
                    value=str(State.vector[i]),

                    width="60px",

                    on_change=lambda v, i=i:
                    State.update_vector(i, v)
                )
            )
        )
    )


def results():

    return rx.cond(

        State.result != {},

        rx.box(

            rx.heading("Resultado"),

            rx.text(
                str(State.result["solution"])
            ),

            rx.heading("Pasos"),

            rx.foreach(

                State.result["steps"],

                lambda step:

                rx.code_block(
                    str(step)
                )
            )
        )
    )


def index():

    return rx.container(

        rx.vstack(

            rx.heading(
                "Método de Gauss-Jordan"
            ),

            rx.select(
                ["2", "3", "4", "5", "6"],

                value="2",

                on_change=State.set_size
            ),

            matrix_inputs(),

            rx.button(
                "Resolver",

                on_click=State.solve
            ),

            results(),

            spacing="4"
        ),

        padding="20px"
    )


app = rx.App()

app.add_page(index)
