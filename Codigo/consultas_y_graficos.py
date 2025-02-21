#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:09:56 2025

@author: yo
@author: yo
"""

#%% IMPORTO LIBRERIAS
import duckdb as dd  
import pandas as pd 
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import seaborn as sns

#%% LEO LAS TABLAS
# obtenemos la ruta del directorio donde se esta ejecutando este codigo
_ruta_actual = os.path.dirname(__file__)

# Ruta a la carpeta TablasOriginales
_ruta_tablas_originales = os.path.join(_ruta_actual, 'TablasModelo')

# Diccionario con las rutas de los archivos CSV
_rutas = {
    "Centros_culturales": os.path.join(_ruta_tablas_originales, 'Centros_culturales.csv'),
    "Poblacion": os.path.join(_ruta_tablas_originales, 'Poblacion.csv'),
    "Establecimientos_educativos": os.path.join(_ruta_tablas_originales, 'Establecimientos_educativos.csv'),
    "Modalidades": os.path.join(_ruta_tablas_originales, 'Modalidades.csv'), 
    "Departamentos": os.path.join(_ruta_tablas_originales, 'Departamentos.csv'),
    "Provincias": os.path.join(_ruta_tablas_originales, 'Provincias.csv'),
    "ee_modalidades": os.path.join(_ruta_tablas_originales, 'ee_modalidades.csv')
}




# guardo en una variable el csv con el nombre, para eso uso globals que genera una variable dinamicamente 
for nombre, ruta in _rutas.items():
    globals()[nombre] = pd.read_csv(ruta)

#%% CONSULTA I VERSION 2

"""
Para cada departamento informar la provincia, cantidad de EE de cada nivel educativo, 
considerando solamente la modalidad común, y cantidad de habitantes por edad según los niveles educativos. 
El orden del reporte debe ser alfabético por provincia y dentro de las provincias, 
descendente por cantidad de escuelas primarias. 
"""

#%% CONSULTA I VERSION 2

"""
Para cada departamento informar la provincia, cantidad de EE de cada nivel educativo, 
considerando solamente la modalidad común, y cantidad de habitantes por edad según los niveles educativos. 
El orden del reporte debe ser alfabético por provincia y dentro de las provincias, 
descendente por cantidad de escuelas primarias. 
"""

"""
Provincias donde el primario dura 6 años:
Formosa, Tucumán, Catamarca, San Juan,
San Luis, Córdoba, Corrientes, 
Entre Ríos, La Pampa, Buenos Aires, 
Chubut y Tierra del Fuego. 

Provincias donde el primario dura 7 años:
Río Negro, Neuquén, Santa Cruz,
Mendoza, Santa Fe, La Rioja, 
Santiago del Estero, Chaco, Misiones, 
Salta, Jujuy, pero tambien en la Ciudad Autónoma de Buenos Aires.
"""

"""
Para cada departamento informar la provincia, cantidad de EE de cada nivel
educativo, considerando solamente la modalidad común, y cantidad de
habitantes por edad según los niveles educativos. El orden del reporte debe
ser alfabético por provincia y dentro de las provincias, descendente por
cantidad de escuelas primarias.
"""

"""
Para cada departamento informar la provincia, cantidad de EE de cada nivel
educativo, considerando solamente la modalidad común, y cantidad de
habitantes por edad según los niveles educativos. El orden del reporte debe
ser alfabético por provincia y dentro de las provincias, descendente por
cantidad de escuelas primarias.
"""
primario6 = (34,90,10,70,74,14,18,30,42,6,26,94)
primario7 = (62,58,78,50,82,46,86,22,54,66,38,2)

Poblacion_jardin = dd.sql(
            """
            SELECT id_prov, id_depto, SUM(Casos) AS Poblacion_jardin
            FROM Poblacion
            WHERE Edad <= 5
            GROUP BY id_prov, id_depto
            """).df()
            
Poblacion_primaria = dd.sql(
            f"""
            WITH primario6 AS (
            SELECT id_prov, id_depto, SUM(Casos) AS Poblacion_primaria
            FROM Poblacion
            WHERE Edad > 5 AND Edad <= 12 AND id_prov IN {primario6}
            GROUP BY id_prov, id_depto),
            
            primario7 AS (SELECT id_prov, id_depto, SUM(Casos) AS Poblacion_primaria
            FROM Poblacion
            WHERE Edad > 5 AND Edad <= 13 AND id_prov IN {primario7}
            GROUP BY id_prov, id_depto)
            
            SELECT *
            FROM primario6
            UNION
            SELECT *
            FROM primario7 
            """).df()
            
Poblacion_secundaria = dd.sql(
            f"""
            WITH secundario6 AS(
            SELECT id_prov, id_depto, SUM(Casos) AS Poblacion_secundaria
            FROM Poblacion
            WHERE Edad > 12 AND Edad <= 18 AND id_prov IN {primario6}
            GROUP BY id_prov, id_depto),
            
            secundario7 AS (SELECT id_prov, id_depto, SUM(Casos) AS Poblacion_secundaria
            FROM Poblacion
            WHERE Edad > 13 AND Edad <= 18 AND id_prov IN {primario7}
            GROUP BY id_prov, id_depto)
            
            SELECT *
            FROM secundario6
            UNION
            SELECT *
            FROM secundario7
            """
            ).df()

Cantidad_ee = dd.sql(
    """
    WITH Conteo AS (
    SELECT ee.id_prov, ee.id_depto, em.id_modalidad, COUNT(*) AS Cantidad
    FROM Establecimientos_educativos AS ee
    INNER JOIN ee_modalidades AS em ON ee.Cueanexo = em.Cueanexo
    GROUP BY id_prov, id_depto, id_modalidad
    ORDER BY id_prov, id_depto, id_modalidad)
    
    SELECT id_prov, id_depto,
    SUM(CASE WHEN id_modalidad IN (0, 1) THEN Cantidad ELSE 0 END) AS Jardines,
    SUM(CASE WHEN id_modalidad = 2 THEN Cantidad ELSE 0 END) AS Primarias,
    SUM(CASE WHEN id_modalidad IN (3, 4) THEN Cantidad ELSE 0 END) AS Secundario
    FROM Conteo
    GROUP BY id_prov, id_depto
    """).df()

Consulta1 = dd.sql(
    """
    WITH prov_depto AS (
    SELECT p.nombre AS Provincia, d.nombre AS Departamento, 
    p.id_prov, d.id_depto
    FROM Departamentos AS d
    INNER JOIN Provincias AS p
    ON d.id_prov = p.id_prov),
    
    Poblaciones AS (
        SELECT pp.id_prov, pp.id_depto, Poblacion_jardin, Poblacion_primaria, Poblacion_secundaria
        FROM Poblacion_jardin AS pj
        INNER JOIN Poblacion_primaria AS pp
        ON pj.id_prov = pp.id_prov AND pj.id_depto = pp.id_depto
        INNER JOIN Poblacion_secundaria AS ps
        ON pj.id_prov = ps.id_prov AND pj.id_depto = ps.id_depto
        )
    
    SELECT Provincia, Departamento, Jardines, Poblacion_jardin, 
    Primarias, Poblacion_primaria, Secundario, Poblacion_secundaria
    FROM prov_depto AS pd
    INNER JOIN Poblaciones AS pob
    ON pd.id_prov = pob.id_prov AND pd.id_depto = pob.id_depto
    INNER JOIN Cantidad_ee AS ce
    ON pd.id_prov = ce.id_prov AND pd.id_depto = ce.id_depto
    
    """).df()

#%% Consulta II

"""
Para cada departamento informar la provincia y la cantidad de CC con
capacidad mayor a 100 personas. El orden del reporte debe ser alfabético
por provincia y dentro de las provincias, descendente por cantidad de CC de
dicha capacidad.
"""

Consulta2 = dd.sql(
    """
    WITH a AS (
    SELECT id_prov, id_depto, COUNT(*) AS Cantidad_mayor_100
    FROM Centros_culturales
    WHERE Capacidad > 100
    GROUP BY id_prov, id_depto)
    SELECT p.nombre, d.nombre, a.Cantidad_mayor_100
    FROM a 
    INNER JOIN Provincias AS p
    ON p.id_prov = a.id_prov
    INNER JOIN Departamentos AS d
    ON d.id_depto = a.id_depto
    GROUP BY p.nombre, d.nombre, Cantidad_mayor_100
    ORDER BY p.nombre ASC, Cantidad_mayor_100 DESC
    """
    ).df()

#%% CONSULTA III

"""
Para cada departamento, indicar provincia, cantidad de CC, cantidad de EE
(de modalidad común) y población total. Ordenar por cantidad EE
descendente, cantidad CC descendente, nombre de provincia ascendente y
nombre de departamento ascendente. No omitir casos sin CC o EE.
"""


Cantidad_cc = dd.sql(
        """
        SELECT id_prov, id_depto, COUNT(*) AS Cantidad_cc
        FROM Centros_culturales
        GROUP BY id_prov, id_depto
        """).df()

Cantidad_ee = dd.sql(
    """
    SELECT id_prov, 0 AS id_depto, COUNT(DISTINCT Cueanexo) AS Cantidad_ee
    FROM Establecimientos_educativos
    WHERE id_prov = 2
    GROUP BY id_prov
    UNION
    SELECT id_prov, id_depto, COUNT(DISTINCT Cueanexo) AS Cantidad_ee
    FROM Establecimientos_educativos
    GROUP BY id_prov, id_depto
    """).df()
    
Poblacion_total = dd.sql(
    """
    SELECT id_prov, 0 AS id_depto, SUM(Casos) AS Personas
    FROM Poblacion
    WHERE id_prov = 2
    GROUP BY id_prov
    UNION
    SELECT id_prov, id_depto, SUM(Casos) AS Personas
    FROM Poblacion
    GROUP BY id_prov, id_depto
    """
    ).df()

Consulta3 = dd.sql(
    """
    WITH prov_depto AS (
    SELECT d.id_prov, d.id_depto, d.nombre AS Departamento, 
    p.nombre AS Provincia
    FROM Departamentos AS d
    INNER JOIN Provincias AS p
    ON d.id_prov = p.id_prov)
    
    SELECT pd.Provincia, pd.Departamento, Cantidad_ee, Cantidad_cc, Personas
    FROM prov_depto AS pd
    LEFT JOIN Cantidad_ee AS ee
    ON pd.id_prov = ee.id_prov AND pd.id_depto = ee.id_depto
    LEFT JOIN Cantidad_cc AS cc
    ON pd.id_prov = cc.id_prov AND pd.id_depto = cc.id_depto
    LEFT JOIN Poblacion_total AS pt
    ON pd.id_prov = pt.id_prov AND pd.id_depto = pt.id_depto
    ORDER BY Cantidad_ee DESC, Cantidad_cc DESC, pd.Provincia ASC, 
    pd.Departamento ASC;
    """
    ).df()
#%% CONSULTA IV

"""
Para cada departamento, indicar provincia y qué dominios de mail se usan
más para los CC.
"""
# EL dominio de un mail es todo lo que hay despues del arroba @
Consulta4 = dd.sql(
    """
    WITH Dominios AS (
    SELECT id_prov, id_depto, LOWER(SPLIT_PART(TRIM(Mail), '@', 2)) AS Dominio
    FROM Centros_culturales),
    
    Frecuencias AS (
    SELECT id_prov, id_depto, Dominio, COUNT(Dominio) AS Frecuencias
    FROM Dominios
    GROUP BY id_prov, id_depto, Dominio),
    
    Max_frecuencia AS (
        SELECT id_prov, id_depto, MAX(Frecuencias) AS Mas_frecuente
        FROM Frecuencias
        GROUP BY id_prov, id_depto)
    
    SELECT p.nombre AS Provincia, d.nombre AS Departamento,
    f.Dominio AS Dominio_mas_frecuente
    FROM Frecuencias AS f
    INNER JOIN Max_frecuencia AS m
    ON f.id_prov = m.id_prov AND f.id_depto = m.id_depto AND f.Frecuencias = m.Mas_frecuente
    INNER JOIN Departamentos AS d
    ON d.id_prov = f.id_prov AND d.id_depto = f.id_depto
    INNER JOIN Provincias AS p
    ON p.id_prov = f.id_prov
    WHERE f.Dominio IS NOT NULL
    """).df()

#%% GRAFICO I

"""
Cantidad de CC por provincia. Mostrarlos ordenados de manera decreciente 
por dicha cantidad. 
"""

visualizacion1 = dd.sql(
    """
    SELECT 
        p.nombre AS provincia,
        COUNT(cc.id_cc) AS cantidad_cc,
        FROM Centros_culturales AS cc
        JOIN Provincias AS p ON cc.id_prov = p.id_prov
        GROUP BY provincia
        ORDER BY cantidad_cc DESC
    """
    ).df()

# Grafico de barras horizontal
plt.figure(figsize=(12, 6))
plt.barh(visualizacion1["provincia"], visualizacion1["cantidad_cc"], color="steelblue")
plt.xlabel("Cantidad de Centros Culturales")
plt.ylabel("Provincia")
plt.title("Cantidad de Centros Culturales por Provincia")
plt.grid(True, axis='x', linestyle='--', alpha=0.7)
plt.gca().invert_yaxis()  
plt.show()


# %% GRAFICO II

"""
Graficar la cantidad de EE de los departamentos en función de la población, 
separando por nivel educativo y su correspondiente grupo etario (identificándolos por colores). 
Se pueden basar en la primera consulta SQL para realizar este gráfico. 
"""

# y = mx + b
def ajuste_lineal(x, y, color, label):
    m, b = np.polyfit(x, y, deg=1)
    x_recta = np.linspace(min(x), max(x), 1000)
    y_pred = m * x_recta + b
    
    plt.scatter(x, y, marker=".", color = color, label = label, alpha = 0.75)
    plt.plot(x_recta, y_pred, color = color)
    
    r2 = r2_score(y, m*x+b)
    
    print(f"r2 {label}: " + str(r2))
    

    
poblacion_jardin = Consulta1["Poblacion_jardin"]
cantidad_jardin = Consulta1["Jardines"]

poblacion_primaria = Consulta1["Poblacion_primaria"]
cantidad_primaria = Consulta1["Primarias"]

poblacion_secundaria = Consulta1["Poblacion_secundaria"]
cantidad_secundaria = Consulta1["Secundario"]

fig, ax = plt.subplots(figsize = (12,7))

ajuste_lineal(poblacion_jardin, cantidad_jardin, "red", "Jardin")
ajuste_lineal(poblacion_primaria, cantidad_primaria, "green", "Primario")
ajuste_lineal(poblacion_secundaria, cantidad_secundaria, "blue", "Secundario")

plt.grid(True)
plt.xlabel("Poblacion", fontsize = 14)
plt.ylabel("Cantidad de establecimientos educativos", fontsize = 16)
plt.title("Cantidad de establecimientos educativos en funcion de la poblacion", fontsize = 16, fontweight = "bold")
plt.legend(loc = "lower right", fontsize = 16)

#%% GRAFICO III

datos = dd.sql(
    """
    SELECT DISTINCT p.nombre, id_depto, COUNT(*) AS Cantidad
    FROM Establecimientos_educativos AS ee
    INNER JOIN Provincias AS p
    ON p.id_prov = ee.id_prov 
    GROUP BY p.nombre, id_depto
    """).df()

medianas = datos.groupby("nombre")["Cantidad"].median()
medianas_ordenadas = medianas.sort_values()

indice = medianas_ordenadas.index

plt.figure(figsize=(10, 6))
sns.boxplot(data=datos, x="nombre", y="Cantidad", order = indice, color = "lightblue")

plt.title("Cantidad de EE por Departamento en cada Provincia", fontsize=16)
plt.xlabel("Provincia", fontsize=12)
plt.ylabel("Cantidad de Establecimientos Educativos", fontsize=12)
plt.xticks(rotation=90)  # Rotar etiquetas del eje x para mejor legibilidad
plt.grid(True)
plt.show()
#%% GRAFICO IV VERSION 1

# por provincia obtener la cant de cc y ee cada 1000 habitantes

# cant habitantes por prov
poblacion_por_provincia = dd.sql("""
                                 SELECT id_prov, SUM(Casos) AS cantidad
                                 FROM Poblacion
                                 GROUP BY id_prov
                                 """).df()
poblacion_por_provincia["cantidad"] = poblacion_por_provincia["cantidad"].astype(int)

# cant cc por prov
cc_por_provincia = dd.sql("""
                            SELECT id_prov, COUNT(*) AS cantidad
                            FROM Centros_culturales
                            GROUP BY id_prov
                          """).df()

# cant ee por prov
ee_por_provincia = dd.sql("""
                            SELECT id_prov, COUNT(*) AS cantidad
                            FROM Establecimientos_educativos
                            GROUP BY id_prov
                          """).df()

# armo tabla con nombre provincia y cantidad de ee y cc cada mil habitantes 
cantidad_eecc_cada_mil = dd.sql("""
                                 SELECT p.id_prov, p.nombre, ((ccp.cantidad*1000) / ppp.cantidad) AS cant_cc_cada_mil, ((eep.cantidad*1000) / ppp.cantidad) AS cant_ee_cada_mil
                                 FROM Provincias p
                                 INNER JOIN cc_por_provincia ccp ON ccp.id_prov = p.id_prov
                                 INNER JOIN poblacion_por_provincia ppp ON ppp.id_prov = p.id_prov 
                                 INNER JOIN ee_por_provincia eep ON eep.id_prov = p.id_prov
                                 ORDER BY cant_ee_cada_mil DESC
                                """).df()


# grafico barras apiladas
plt.figure(figsize=(12, 6))

plt.bar(cantidad_eecc_cada_mil["nombre"], cantidad_eecc_cada_mil["cant_ee_cada_mil"], label="Establecimientos Educativos", color="royalblue")
plt.bar(cantidad_eecc_cada_mil["nombre"], cantidad_eecc_cada_mil["cant_cc_cada_mil"], bottom=cantidad_eecc_cada_mil["cant_ee_cada_mil"], label="Centros Culturales", color="orange")

plt.xlabel("Provincia")
plt.ylabel("Cantidad cada 1000 habitantes")
plt.title("Relación entre Centros Culturales y Establecimientos Educativos cada 1000 habitantes")
plt.xticks(rotation=45, ha="right") 
plt.legend()  

plt.show()



#%% GRAFICO 4 VERSION 2
"""
Relación entre la cantidad de CC cada mil habitantes y de EE cada mil
habitantes
"""

data = dd.sql(
    """
    SELECT Provincia, Departamento, 
    (Cantidad_ee / Poblacion) * 1000 AS EE_cada_mil,
    (Cantidad_cc / Poblacion) * 1000 AS CC_cada_mil
    FROM Consulta3
    WHERE Cantidad_ee IS NOT NULL AND Cantidad_cc IS NOT NULL
    AND Poblacion IS NOT NULL;
    """
    ).df()


plt.figure(figsize=(8, 6))
sns.scatterplot(data = data, x ="EE_cada_mil", y="CC_cada_mil")

plt.title("Relación entre CC cada mil habitantes y EE cada mil habitantes", fontsize=16)
plt.xlabel("EE cada mil habitantes", fontsize = 14)
plt.ylabel("CC cada mil habitantes", fontsize = 14)
plt.grid(True)
plt.show()

#%%