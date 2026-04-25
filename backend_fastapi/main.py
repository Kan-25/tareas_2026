from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Analizador Matemático - Métodos Numéricos")

# --- MODELOS DE ENTRADA (JSON) ---

class FalsaPosicionInput(BaseModel):
    xi: float
    xd: float
    tol: float

class BairstowInput(BaseModel):
    coefs: List[float] # Coeficientes del polinomio [a0, a1, a2... an]
    r: float
    s: float
    tol: float
    max_iter: int = 100

# ENDPOINTS

@app.post("/falsa-posicion") #metodo de falsa posicion
def post_falsa_posicion(data: FalsaPosicionInput):
    # Definición de la función
    def f(x): 
        return x**2 - 5
    
    xi, xd = data.xi, data.xd
    f_xi, f_xd = f(xi), f(xd)

    # Verificación inicial: Teorema de Bolzano
    if f_xi * f_xd >= 0:
        raise HTTPException(
            status_code=400, 
            detail="Error: No hay cambio de signo en el intervalo [xi, xd]. f(xi)*f(xd) debe ser < 0."
        )
    
    iteraciones = []
    xr = xi
    ea = 100
    
    for i in range(1, 101): # Máximo 100 iteraciones por seguridad
        xr_anterior = xr
        f_xi, f_xd = f(xi), f(xd)
        
        # Fórmula: Unión de f(xi) y f(xd) con línea recta
        denominador = f_xi - f_xd
        if denominador == 0: break
            
        xr = xd - (f_xd * (xi - xd)) / denominador
        
        if xr != 0: 
            ea = abs((xr - xr_anterior) / xr) * 100
        
        # Guardar cada iteración para la salida JSON
        iteraciones.append({
            "iter": i, 
            "xi": round(xi, 6), 
            "xd": round(xd, 6), 
            "xr": round(xr, 6), 
            "f_xr": round(f(xr), 6),
            "ea": round(ea, 6)
        })
        
        # Decidir nuevo intervalo
        if f(xi) * f(xr) < 0: 
            xd = xr
        else: 
            xi = xr
        
        if ea < data.tol: 
            break

    return {
        "datos_entrada": data,
        "iteraciones": iteraciones,
        "resultado_final": xr,
        "explicacion": "El método de Falsa Posición (Regula Falsi) aproxima la raíz conectando f(xi) y f(xd) mediante una línea recta. El punto donde esta línea cruza el eje x es la nueva aproximación xr."
    }
@app.post("/bairstow") #metodo bairtow
def post_bairstow(data: BairstowInput):
    a = data.coefs
    r, s = data.r, data.s
    n = len(a) - 1
    
    if n < 2:
        raise HTTPException(status_code=400, detail="El polinomio debe ser al menos de grado 2")

    iteraciones = []
    
    for i in range(data.max_iter):
        b = [0] * (n + 1)
        c = [0] * (n + 1)
        
        # Llenado de b
        b[n] = a[n]
        b[n-1] = a[n-1] + r * b[n]
        for j in range(n-2, -1, -1):
            b[j] = a[j] + r * b[j+1] + s * b[j+2]
            
        # Llenado de c
        c[n] = b[n]
        c[n-1] = b[n-1] + r * c[n]
        for j in range(n-2, 1, -1): #para evitar índices menores a 1 innecesarios
            c[j] = b[j] + r * c[j+1] + s * c[j+2]
        
        # Si n=2, c[3] no existe. Usamos 0 como valor por defecto para el cálculo del sistema.
        c3 = c[3] if n >= 3 else 0
        c2 = c[2]
        c1 = c[1]
        
        det = (c2 * c2) - (c3 * c1)
        
        if det == 0:
            raise HTTPException(status_code=500, detail="Determinante cero: el método no converge.")
            
        dr = (-(b[1] * c2) + (b[0] * c3)) / det
        ds = (-(b[0] * c2) + (b[1] * c1)) / det
        
        r += dr
        s += ds
        
        err_r = abs(dr/r)*100 if r != 0 else 0
        err_s = abs(ds/s)*100 if s != 0 else 0
        
        iteraciones.append({
            "iter": i + 1, 
            "r": round(r, 6), 
            "s": round(s, 6), 
            "err_r": round(err_r, 6),
            "err_s": round(err_s, 6)
        })
        
        if err_r < data.tol and err_s < data.tol: 
            break

    return {
        "datos_entrada": data.dict(),
        "iteraciones": iteraciones,
        "resultado_final": {
            "r": round(r, 6), 
            "s": round(s, 6), 
            "factor": f"x² - ({round(r,4)})x - ({round(s,4)})"
        },
        "explicacion": "El método de Bairstow extrae factores cuadráticos mediante división sintética doble, permitiendo hallar raíces complejas y reales."
    }