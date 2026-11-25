"""Tests del cálculo del índice. Ejecutar desde la carpeta del proyecto:  python -m pytest"""
import pandas as pd

from src.indice import calcular_indice, normalizar

# Datos de ejemplo pequeños: 3 países y 2 indicadores
DATOS = pd.DataFrame({"talento": [10, 20, 30], "coste": [5, 10, 15]}, index=["A", "B", "C"])
INDICADORES = pd.DataFrame({"id": ["talento", "coste"], "pilar": ["Talento", "Costes"], "sentido": [1, -1]})


def test_normalizar_va_de_0_a_100():
    nota = normalizar(DATOS["talento"], 1)
    assert nota.min() == 0 and nota.max() == 100


def test_los_costes_se_invierten():
    # En costes, el país más barato (A) debe sacar la nota más alta
    nota = normalizar(DATOS["coste"], -1)
    assert nota["A"] == 100 and nota["C"] == 0


def test_los_pesos_cambian_el_ganador():
    # Si solo importa el talento, gana C (más talento); si solo importan los costes, gana A (más barato)
    solo_talento = calcular_indice(DATOS, INDICADORES, {"Talento": 10, "Costes": 0})
    solo_costes = calcular_indice(DATOS, INDICADORES, {"Talento": 0, "Costes": 10})
    assert solo_talento.index[0] == "C"
    assert solo_costes.index[0] == "A"


def test_quitar_indicadores():
    # Si se desmarca el único indicador de Costes, ese pilar no cuenta
    resultado = calcular_indice(DATOS, INDICADORES, {"Talento": 5, "Costes": 5}, activos=["talento"])
    assert resultado.index[0] == "C"


def test_puestos_del_1_al_n():
    resultado = calcular_indice(DATOS, INDICADORES, {"Talento": 7, "Costes": 3})
    assert sorted(resultado["puesto"]) == [1, 2, 3]
