from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import math

app = FastAPI(title="API de Diferenciacion Numerica")

# Permitir conexiones desde cualquier origen (necesario para acceder via WiFi/LAN)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nombres y funciones matematicas permitidas para evaluar f(x)
ALLOWED_NAMES = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
ALLOWED_NAMES.update({
    "abs": abs,
    "pi": math.pi,
    "e": math.e,
})


class CalculationRequest(BaseModel):
    function_str: str
    x_val: float
    h_val: float
    method: str  # "adelante", "atras", "central" o "todos"

    @field_validator("function_str")
    @classmethod
    def validar_funcion(cls, v):
        if not v or not v.strip():
            raise ValueError("La funcion no puede estar vacia")
        prohibidos = ["__", "import", "lambda", "exec", "eval", "open", "os", "sys"]
        bajo = v.lower()
        for p in prohibidos:
            if p in bajo:
                raise ValueError(f"La funcion contiene un termino no permitido: '{p}'")
        return v

    @field_validator("h_val")
    @classmethod
    def validar_h(cls, v):
        if v == 0:
            raise ValueError("El paso h no puede ser 0")
        if v < 0:
            raise ValueError("El paso h debe ser positivo")
        return v

    @field_validator("method")
    @classmethod
    def validar_metodo(cls, v):
        if v not in ("adelante", "atras", "central", "todos"):
            raise ValueError("Metodo invalido. Use: adelante, atras, central o todos")
        return v


def safe_eval(func_str: str, x: float) -> float:
    """Evalua f(x) en un entorno restringido."""
    contexto = dict(ALLOWED_NAMES)
    contexto["x"] = x
    try:
        resultado = eval(func_str, {"__builtins__": {}}, contexto)
    except ZeroDivisionError:
        raise ValueError("Division por cero al evaluar la funcion")
    except NameError as e:
        raise ValueError(f"Nombre no reconocido en la funcion: {e}")
    except SyntaxError:
        raise ValueError("Sintaxis invalida en la funcion")

    if isinstance(resultado, complex):
        raise ValueError("La funcion produjo un numero complejo en este punto")
    if not isinstance(resultado, (int, float)):
        raise ValueError("La funcion no produjo un numero valido")
    if math.isnan(resultado) or math.isinf(resultado):
        raise ValueError("La funcion produjo un valor indefinido (NaN o infinito)")
    return float(resultado)


def calcular_metodo(func_str: str, x: float, h: float, metodo: str) -> float:
    if metodo == "adelante":
        fx = safe_eval(func_str, x)
        fxh = safe_eval(func_str, x + h)
        return (fxh - fx) / h
    elif metodo == "atras":
        fx = safe_eval(func_str, x)
        fxmh = safe_eval(func_str, x - h)
        return (fx - fxmh) / h
    elif metodo == "central":
        fxh = safe_eval(func_str, x + h)
        fxmh = safe_eval(func_str, x - h)
        return (fxh - fxmh) / (2 * h)
    else:
        raise ValueError("Metodo no valido")


def generar_grafica(func_str: str, x: float, h: float):
    puntos_x, puntos_y = [], []
    rango = max(abs(h) * 6, 1.0)
    n_puntos = 60
    for i in range(n_puntos + 1):
        xi = x - rango + (2 * rango * i / n_puntos)
        try:
            yi = safe_eval(func_str, xi)
            puntos_x.append(xi)
            puntos_y.append(yi)
        except ValueError:
            pass
    return {"x": puntos_x, "y": puntos_y}


@app.get("/")
def root():
    return {"status": "ok", "mensaje": "API de Diferenciacion Numerica activa"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/calculate/")
def calculate_derivative(req: CalculationRequest):
    try:
        x = req.x_val
        h = req.h_val
        func_str = req.function_str.strip()

        fx_centro = safe_eval(func_str, x)

        if req.method == "todos":
            resultados = {}
            for m in ("adelante", "atras", "central"):
                try:
                    resultados[m] = calcular_metodo(func_str, x, h, m)
                except ValueError as e:
                    resultados[m] = None
                    resultados[f"{m}_error"] = str(e)

            return {
                "x": x,
                "h": h,
                "f_x": fx_centro,
                "resultados": resultados,
                "grafica": generar_grafica(func_str, x, h),
            }

        resultado = calcular_metodo(func_str, x, h, req.method)

        return {
            "resultado": resultado,
            "metodo": req.method,
            "x": x,
            "h": h,
            "f_x": fx_centro,
            "grafica": generar_grafica(func_str, x, h),
        }
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}
