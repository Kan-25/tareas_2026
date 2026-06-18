from nicegui import ui
import requests
import os

BACKEND_HOST = os.environ.get("BACKEND_HOST", "backend")
BACKEND_URL = f"http://{BACKEND_HOST}:8000/calculate/"

METODOS_LABELS = {
    "adelante": "Diferencia hacia Adelante",
    "atras": "Diferencia hacia Atrás",
    "central": "Diferencia Central",
    "todos": "Comparar los 3 métodos a la vez",
}

FORMULAS = {
    "adelante": "f'(x) ≈ [f(x+h) − f(x)] / h",
    "atras": "f'(x) ≈ [f(x) − f(x−h)] / h",
    "central": "f'(x) ≈ [f(x+h) − f(x−h)] / (2h)",
    "todos": "Se calcularán las 3 fórmulas simultáneamente para evaluar cuál es más exacta.",
}

ui.add_head_html('<style>.titulo{font-family: "Segoe UI", sans-serif;}</style>')

# --- CONTENEDORES PRINCIPALES ---
# Estructuramos la página de manera limpia y centrada
with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-4'):
    ui.label('Diferenciación Numérica').classes('text-3xl font-bold titulo text-center w-full text-blue-700')
    ui.label('Cálculo interactivo de derivadas aproximadas mediante diferencias finitas').classes(
        'text-sm text-gray-500 text-center w-full -mt-3 mb-2'
    )

    # 1. TARJETA DE CONFIGURACIÓN / FORMULARIO DE ENTRADAS
    with ui.card().classes('w-full shadow-md p-6 bg-white rounded-xl border border-gray-100'):
        ui.label('📝 Parámetros de la Derivada').classes('text-lg font-bold text-gray-700 mb-2')
        
        func_input = ui.input(
            label='Función Matemática f(x)',
            value='x**2',
            placeholder='Ej: sin(x), x**2 + 3*x, exp(x)',
        ).classes('w-full').props('outlined clearable hint="Usa la variable \'x\'. Ejemplos: x**2, sin(x), exp(-x)" prepend-inner-icon="functions"')

        with ui.row().classes('w-full gap-4 mt-2'):
            x_input = ui.number(
                label='Punto de evaluación (x)', 
                value=2.0, 
                format='%.6f'
            ).classes('flex-1').props('outlined hint="El valor numérico de x donde deseas hallar la pendiente" prepend-inner-icon="pin"')
            
            h_input = ui.number(
                label='Tamaño del paso (h)', 
                value=0.5, 
                format='%.6f', 
                min=0.0000001
            ).classes('flex-1').props('outlined hint="El incremento (un valor más pequeño suele ser más exacto)" prepend-inner-icon="grid_3x3"')

        method_select = ui.select(
            METODOS_LABELS, 
            value='central', 
            label='Método Matemático'
        ).classes('w-full mt-2').props('outlined prepend-inner-icon="layers"')

        # Caja elegante para mostrar la fórmula matemática activa
        with ui.row().classes('w-full items-center bg-blue-50 p-3 rounded-lg border border-blue-100 mt-2'):
            ui.icon('info', color='primary').classes('text-lg mr-1')
            formula_label = ui.label(FORMULAS['central']).classes('text-sm text-blue-900 font-medium')

        ui.label(
            '💡 Operadores válidos: +, -, *, /, ** (potencia). Funciones: sin, cos, tan, exp, log, sqrt, abs, pi, e.'
        ).classes('text-xs text-gray-400 mt-2')

        # Botón principal de calcular (estilizado y bien ubicado)
        btn_calcular = ui.button(
            'Calcular Derivada', 
            icon='calculate'
        ).classes('w-full py-3 text-base font-semibold mt-4 text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow')

    # 2. TARJETAS DE RESULTADO Y GRÁFICA (Dinámicas)
    resultado_card = ui.card().classes('w-full shadow-md p-6 rounded-xl border border-gray-100')
    grafica_card = ui.card().classes('w-full shadow-md p-6 rounded-xl border border-gray-100')


# --- LÓGICA DE CONTROLADORES Y FUNCIONES ---

def actualizar_formula(e):
    formula_label.set_text(FORMULAS[method_select.value])

method_select.on_value_change(actualizar_formula)

def validar_entradas():
    errores = []
    if not func_input.value or not func_input.value.strip():
        errores.append('Por favor, ingresa una función matemática f(x).')
    if x_input.value is None:
        errores.append('Falta ingresar el punto de evaluación x.')
    if h_input.value is None:
        errores.append('Falta ingresar el tamaño del paso h.')
    elif h_input.value == 0:
        errores.append('El paso h no puede ser exactamente 0.')
    elif h_input.value < 0:
        errores.append('El paso h debe ser un número positivo.')
    return errores

def mostrar_error(mensaje):
    resultado_card.clear()
    grafica_card.clear()
    with resultado_card:
        with ui.row().classes('items-center gap-2 text-red-600'):
            ui.icon('error', size='md')
            ui.label('Error detectado').classes('text-lg font-bold')
        ui.label(mensaje).classes('text-red-500 text-sm mt-1 bg-red-50 p-3 rounded-lg w-full border border-red-100')

def dibujar_grafica(grafica, x_val, resultados):
    grafica_card.clear()
    if not grafica or not grafica.get('x'):
        return
    with grafica_card:
        ui.label('📈 Gráfica de la Curva f(x)').classes('text-lg font-bold text-gray-700 mb-2')
        fig = {
            'data': [
                {
                    'x': grafica['x'],
                    'y': grafica['y'],
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'f(x)',
                    'line': {'color': '#2563eb', 'width': 3},
                },
            ],
            'layout': {
                'margin': {'l': 40, 'r': 20, 't': 20, 'b': 40},
                'height': 350,
                'hovermode': 'closest',
                'shapes': [
                    {
                        'type': 'line',
                        'x0': x_val, 'x1': x_val,
                        'y0': min(grafica['y']), 'y1': max(grafica['y']),
                        'line': {'color': '#ef4444', 'dash': 'dot', 'width': 2},
                    }
                ],
            },
        }
        ui.plotly(fig).classes('w-full')

def on_calculate():
    errores = validar_entradas()
    if errores:
        mostrar_error(' '.join(errores))
        return

    payload = {
        'function_str': func_input.value.strip(),
        'x_val': float(x_input.value),
        'h_val': float(h_input.value),
        'method': method_select.value,
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError:
        mostrar_error('No se pudo conectar con el servidor backend. Asegúrate de que FastAPI esté corriendo en Docker.')
        return
    except requests.exceptions.Timeout:
        mostrar_error('La solicitud tardó demasiado. El servidor backend está colgado.')
        return
    except Exception as e:
        mostrar_error(f'Error inesperado de red: {e}')
        return

    if 'error' in data:
        mostrar_error(data['error'])
        return

    # Renderizar los resultados de forma clara y vistosa
    resultado_card.clear()
    with resultado_card:
        ui.label('📊 Resultado del Análisis').classes('text-lg font-bold text-gray-700 mb-2')
        
        with ui.row().classes('w-full justify-between items-center bg-gray-50 p-3 rounded-lg border border-gray-200'):
            ui.label('Valor real de la función original en ese punto:').classes('text-sm text-gray-600')
            ui.label(f"f({data['x']}) = {data['f_x']:.6f}").classes('text-base font-semibold text-gray-800')

        if method_select.value == 'todos':
            resultados = data['resultados']
            ui.label('Comparativa de resultados según el método:').classes('text-sm font-medium text-gray-600 mt-3')
            with ui.column().classes('w-full gap-2 mt-1'):
                for m in ('adelante', 'atras', 'central'):
                    val = resultados.get(m)
                    with ui.row().classes('w-full justify-between items-center bg-white p-2.5 rounded-lg border border-gray-100 shadow-sm'):
                        ui.label(METODOS_LABELS[m]).classes('text-sm font-medium text-gray-700')
                        if val is None:
                            ui.label(f"Error ({resultados.get(m + '_error', 'Desconocido')})").classes('text-sm text-red-500 font-semibold')
                        else:
                            ui.label(f"{val:.6f}").classes('text-base font-bold text-blue-600')
        else:
            with ui.column().classes('w-full items-center mt-4 bg-blue-50/40 p-4 rounded-xl border border-blue-100'):
                ui.label(f"Derivada aproximada ({METODOS_LABELS[method_select.value]}):").classes('text-sm text-gray-500')
                ui.label(f"f'({data['x']}) ≈ {data['resultado']:.6f}").classes('text-3xl font-extrabold text-blue-600 tracking-tight mt-1')
                ui.label(FORMULAS[method_select.value]).classes('text-xs text-gray-400 italic mt-2')

    dibujar_grafica(data.get('grafica'), data['x'], None)

# Asignamos el evento click al botón de calcular
btn_calcular.on_click(on_calculate)

# Mensaje inicial por defecto antes de calcular
with resultado_card:
    ui.label('💡 Modifica los valores superiores y presiona "Calcular Derivada" para ver los resultados aquí.').classes('text-gray-400 text-sm text-center py-4 w-full')

ui.run(host='0.0.0.0', port=8080, title='Diferenciación Numérica', reload=False)