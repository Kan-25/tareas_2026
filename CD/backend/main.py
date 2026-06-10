from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np

app = FastAPI()


class MatrixRequest(BaseModel):
    matrix: List[List[float]]
    vector: List[float]


def gauss_jordan(A, b):
    A_original = np.array(A, dtype=float)
    b_original = np.array(b, dtype=float)

    A = A_original.copy()
    b = b_original.copy()
    n = len(b)

    augmented = np.hstack([A, b.reshape(-1, 1)])
    steps = []
    row = 0

    for col in range(n):
        pivot = max(range(row, n), key=lambda r: abs(augmented[r][col]))

        if abs(augmented[pivot][col]) < 1e-10:
            continue

        if pivot != row:
            augmented[[row, pivot]] = augmented[[pivot, row]]

        augmented[row] = augmented[row] / augmented[row][col]

        for r in range(n):
            if r != row:
                augmented[r] = augmented[r] - augmented[r][col] * augmented[row]

        augmented[np.abs(augmented) < 1e-10] = 0
        steps.append(np.round(augmented.copy(), 2).tolist())
        row += 1

        if row == n:
            break

    rank_A = np.linalg.matrix_rank(A_original)
    rank_aug = np.linalg.matrix_rank(
        np.hstack([A_original, b_original.reshape(-1, 1)])
    )

    final_matrix = np.round(augmented, 2).tolist()

    if rank_A < rank_aug:
        return {
            "solution": [],
            "solution_type": "Sin Solución",
            "steps": steps,
            "final_matrix": final_matrix,
        }

    if rank_A < n:
        return {
            "solution": [],
            "solution_type": "Infinitas Soluciones",
            "steps": steps,
            "final_matrix": final_matrix,
        }

    solution = np.round(augmented[:, -1], 2).tolist()

    print("SOLUCION:", solution)
    print("MATRIZ:", final_matrix)

    return {
        "solution": solution,
        "solution_type": "Solución Única",
        "steps": steps,
        "final_matrix": final_matrix,
    }


@app.post("/gauss-jordan")
def solve(data: MatrixRequest):
    return gauss_jordan(data.matrix, data.vector)