# Progra_Avanzada_Entrega_Parcial

# 🛣️ Dashboard de Análisis de Fatalidades en Siniestros de Tránsito (Perú, 2021-2023)

Este proyecto implementa una aplicación interactiva (Dashboard) utilizando **Streamlit** y **Altair** para visualizar y analizar los datos de personas involucradas en siniestros de tránsito fatales en Perú entre 2021 y 2023.

El objetivo principal es identificar patrones, tendencias geográficas y demográficas de las víctimas fatales para apoyar la toma de decisiones en políticas de seguridad vial.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3.x:** Lenguaje de programación principal.
* **Streamlit:** Framework para la creación de la aplicación web interactiva (dashboard).
* **Pandas:** Manipulación, limpieza y preprocesamiento de los datos (gestión de `NULL`s, corrección de codificación).
* **Altair:** Biblioteca de visualización declarativa para generar gráficos estadísticos y responsivos.

---

## 💾 Fuente de Datos

Los datos provienen del dataset **"PERSONAS INVOLUCRADAS EN SINIESTROS DE TRÁNSITO FATALES 2021-2023 (PRELIMINAR)"**, proporcionado por el **Observatorio Nacional de Seguridad Vial (ONVS)**.

* **Nombre del Archivo Requerido:** `BBDD ONSV - PERSONAS 2021-2023.xlsx - PERSONAS INVOLUCRADAS.csv`
* **Alcance:** El dashboard se enfoca principalmente en los registros donde la variable `GRAVEDAD` es **'FALLECIDO'**.

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para levantar la aplicación localmente:

### 1. Requisitos Previos

Asegúrate de tener Python instalado en tu sistema.

### 2. Clonar el Repositorio

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd <nombre_de_tu_repositorio>

### 3. Instalar Dependencias de Python

El archivo principal (`app.py`) requiere las siguientes librerías:

```bash
pip install streamlit pandas altair numpy

### 4. Colocar el Archivo de Datos

`BBDD ONSV - PERSONAS 2021-2023.xlsx - PERSONAS INVOLUCRADAS.csv`

### 5. Ejecutar la Aplicación Streamlit

```bash
streamlit run app.py
---

## 📊 Visualizaciones Clave

El dashboard presenta cuatro gráficos principales, con un filtro lateral para segmentar por año (aplicable a los gráficos 2, 3 y 4):

1.  **Tendencia Anual de la Gravedad:** Evolución del total de personas involucradas (Fallecidos, Lesionados, Ilesos) por año.
2.  **Top 10 Departamentos con Mayor Cantidad de Fallecidos:** Identificación de las zonas geográficas de alta siniestralidad fatal.
3.  **Fallecidos por Clase de Siniestro:** Distribución de fatalidades por tipo de evento (Choque, Atropello, Volcadura, etc.).
4.  **Fallecidos por Rango de Edad y Sexo:** Análisis demográfico para identificar los grupos más vulnerables (se incluye la categoría 'EDAD DESCONOCIDA' para rastrear datos faltantes).

---

## 🧹 Notas de Preprocesamiento

El código (`app.py`) incluye una robusta función de preprocesamiento (`load_data`) que realiza:

1. **Corrección de Codificación:** Arreglo de acentos y caracteres especiales mal leídos (`Ã‘` -> `Ñ`, `Ã\x93` -> `Ó`).
2. **Limpieza de Edad:** Reemplazo de 'NO INDICA' por `NaN` y posterior imputación categórica a 'EDAD DESCONOCIDA' para el análisis de distribución.
3. **Filtro:** Creación de un subconjunto (`df_fallecido`) para análisis focalizado en la gravedad 'FALLECIDO'.

