import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIGURACIÓN: =================
ARCHIVO = 'datos_limpios.csv'
TITULO = 'Ventas cadena de productos'                      
DESCRIPCION = 'Contiene datos sintéticos de ventas de una cadena de productos con presencia en Perú, Chile y Argentina, incluyendo información de clientes, fechas, ubicación, productos, cantidades, precios, costos y métodos de pago. '  # <- tu descripción
AUTOR = 'Sosa Paola'              
KAGGLE = 'https://www.kaggle.com/datasets/edwertimudo/ventas-cadena-de-productos-peru-chile-y-argentina'
COL_CAT = 'Categoria'       # columna de categorías
COL_NUM = 'Venta_Total'     # columna numérica principal
COL_NUM2 = 'Cantidad'       # segunda columna numérica
COLORES = {'Electrónica': '#1f77b4', 'Hogar': '#2ca02c', 'Ropa': '#ff7f0e'}
# =========================================================================

st.set_page_config(page_title=TITULO, page_icon='📊', layout='wide')

@st.cache_data
def cargar_datos():
    return pd.read_csv(ARCHIVO)

df = cargar_datos()

st.title(f'📊 {TITULO}')
st.write(DESCRIPCION)

# ---------- BARRA LATERAL: filtros e información ----------
st.sidebar.header('Filtros')

categorias = sorted(df[COL_CAT].dropna().astype(str).unique())
sel_cat = st.sidebar.multiselect(f'{COL_CAT} (vacío = todas)', categorias)

minimo = float(df[COL_NUM].min())
maximo = float(df[COL_NUM].max())
rango = st.sidebar.slider(COL_NUM, minimo, maximo, (minimo, maximo))

st.sidebar.markdown('---')
st.sidebar.markdown(f'**Autor:** {AUTOR}  \n**Datos:** [Kaggle]({KAGGLE})')

df_f = df[df[COL_NUM].between(rango[0], rango[1])]
if sel_cat:
    df_f = df_f[df_f[COL_CAT].astype(str).isin(sel_cat)]

if df_f.empty:
    st.warning('No hay datos con estos filtros. Cambia la selección.')
    st.stop()

# ---------- INDICADORES (KPI) ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric('Registros', f'{len(df_f):,}',
          delta=f'{len(df_f) / len(df) * 100:.1f}% del total',
          delta_color='off')
k2.metric(f'Promedio de {COL_NUM}', f'{df_f[COL_NUM].mean():,.2f}',
          delta=f'{df_f[COL_NUM].mean() - df[COL_NUM].mean():+,.2f} vs. total')
k3.metric(f'Mediana de {COL_NUM}', f'{df_f[COL_NUM].median():,.2f}')
k4.metric('Categoría más frecuente', str(df_f[COL_CAT].mode()[0]))

# ---------- GRÁFICOS ----------
top10 = df_f[COL_CAT].value_counts().head(10).index
df_top = df_f[df_f[COL_CAT].isin(top10)]

izq, der = st.columns(2)

conteo = df_top[COL_CAT].value_counts().reset_index()
conteo.columns = [COL_CAT, 'cantidad']
fig1 = px.bar(conteo, x='cantidad', y=COL_CAT, orientation='h',
              color=COL_CAT, color_discrete_map=COLORES,
              title=f'Registros por {COL_CAT} (10 más frecuentes)',
              labels={'cantidad': 'Cantidad de registros'})
fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
izq.plotly_chart(fig1)

fig2 = px.histogram(df_f, x=COL_NUM, nbins=30,
                    color_discrete_sequence=['#6a3d9a'],
                    title=f'Distribución de {COL_NUM}')
fig2.update_layout(yaxis_title='Cantidad de registros')
der.plotly_chart(fig2)

izq2, der2 = st.columns(2)
fig3 = px.box(df_top, x=COL_CAT, y=COL_NUM,
              color=COL_CAT, color_discrete_map=COLORES,
              title=f'{COL_NUM} según {COL_CAT}')
fig3.update_layout(showlegend=False)
izq2.plotly_chart(fig3)

muestra = df_f.sample(min(len(df_f), 3000), random_state=1)
r = df_f[COL_NUM].corr(df_f[COL_NUM2])
fig4 = px.scatter(muestra, x=COL_NUM2, y=COL_NUM, opacity=0.3,
                  color=COL_CAT, color_discrete_map=COLORES,
                  title=f'Relación entre {COL_NUM2} y {COL_NUM} (r = {r:.2f})')
der2.plotly_chart(fig4)

# ---------- TABLA Y DESCARGA ----------
with st.expander('Ver los datos filtrados'):
    st.dataframe(df_f)

st.download_button('⬇ Descargar datos filtrados (CSV)',
                   data=df_f.to_csv(index=False).encode('utf-8'),
                   file_name='datos_filtrados.csv', mime='text/csv')

# ---------- CONCLUSIONES ----------
st.subheader('Conclusiones')
st.markdown('''
- **Promedio y mediana por categoría:** Electrónica presenta el promedio más alto ($761,58) y una mediana de $692,32, con un promedio $378,80 por encima del total. Ropa tiene un promedio de $200,22 y una mediana de $179,85, mientras que Hogar registra $198,15 y $174,24, respectivamente. Sus promedios están $182,56 y $184,63 por debajo del total.
- **Comparación del gráfico de caja:** Ropa y Hogar presentan distribuciones bastante similares, mientras que Electrónica tiene valores de venta mucho más elevados. También se observan valores atípicos, que representan el 10,5 % de los registros según el análisis de la Actividad 2.2.
- **Relación entre cantidad y venta:** con todos los datos juntos, la correlación entre `Cantidad` y `Venta_Total` es de 0,50. Al filtrar por categoría, aumenta a 0,78 en Ropa y Hogar, y a 0,80 en Electrónica. Esto indica que la relación entre cantidad y venta es más fuerte dentro de cada categoría, posiblemente porque los precios de los productos varían entre categorías y afectan la relación al analizar todos los datos juntos.
''')
