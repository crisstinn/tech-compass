"""Perfiles de empresa predefinidos.

Cada perfil fija los pesos (de 0 a 10) de los cuatro pilares,
para que el usuario no tenga que mover los sliders a mano.
"""

PERFILES = {
    "equilibrado": {
        "nombre": "Equilibrado (todo igual)",
        "pesos": {"Talento": 5, "Innovación": 5, "Costes": 5, "Entorno": 5},
    },
    "startup": {
        "nombre": "Startup tecnológica",
        "pesos": {"Talento": 8, "Innovación": 6, "Costes": 7, "Entorno": 3},
    },
    "expansion": {
        "nombre": "Empresa en expansión",
        "pesos": {"Talento": 5, "Innovación": 5, "Costes": 4, "Entorno": 8},
    },
    "id": {
        "nombre": "Centro de I+D",
        "pesos": {"Talento": 7, "Innovación": 10, "Costes": 2, "Entorno": 4},
    },
    "costes": {
        "nombre": "Reducir costes",
        "pesos": {"Talento": 3, "Innovación": 2, "Costes": 10, "Entorno": 4},
    },
    "talento": {
        "nombre": "Buscar talento tecnológico",
        "pesos": {"Talento": 10, "Innovación": 4, "Costes": 4, "Entorno": 3},
    },
}
