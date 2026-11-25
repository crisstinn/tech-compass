"""API REST con Flask-RESTful (como en la práctica de clase).

Permite consultar el ranking desde otro programa, sin abrir la web:
    GET /api/ranking                  -> ranking con pesos iguales
    GET /api/ranking/<perfil>         -> ranking de un perfil (startup, id, costes...)
    GET /api/pais/<codigo>            -> ficha de un país (por ejemplo ESP)
"""
from flask_restful import Api, Resource, abort

from src.indice import calcular_indice
from src.perfiles import PERFILES


def crear_api(server, datos, indicadores, nombres, pilares):
    api = Api(server)

    def ranking_de(perfil):
        if perfil not in PERFILES:
            abort(404, message=f"No existe el perfil '{perfil}'. Opciones: {list(PERFILES)}")
        return calcular_indice(datos, indicadores, PERFILES[perfil]["pesos"])

    class Ranking(Resource):
        def get(self, perfil="equilibrado"):
            resultado = ranking_de(perfil)
            return {
                "perfil": PERFILES[perfil]["nombre"],
                "pesos": PERFILES[perfil]["pesos"],
                "ranking": [{"puesto": int(fila["puesto"]), "codigo": codigo, "pais": nombres[codigo],
                             "nota": round(float(fila["nota"]), 2)}
                            for codigo, fila in resultado.iterrows()],
            }

    class Pais(Resource):
        def get(self, codigo):
            codigo = codigo.upper()
            if codigo not in nombres:
                abort(404, message=f"No existe el país '{codigo}'. Usa el código de 3 letras, por ejemplo ESP.")
            fila = ranking_de("equilibrado").loc[codigo]
            return {
                "codigo": codigo,
                "pais": nombres[codigo],
                "puesto": int(fila["puesto"]),
                "nota": round(float(fila["nota"]), 2),
                "pilares": {p: round(float(fila[p]), 2) for p in pilares},
                "indicadores": {i: round(float(datos.loc[codigo, i]), 3) for i in indicadores["id"]},
            }

    api.add_resource(Ranking, "/api/ranking", "/api/ranking/<string:perfil>")
    api.add_resource(Pais, "/api/pais/<string:codigo>")
