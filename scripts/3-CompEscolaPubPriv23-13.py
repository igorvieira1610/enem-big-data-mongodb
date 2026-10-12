import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']

def processar_dados_enem(enem_db, ano):
    collection = db[enem_db]

    projecao = {
        '_id': 0,
        'TP_ESCOLA': 1,
        'NU_NOTA_CN': 1, 'NU_NOTA_CH': 1, 'NU_NOTA_LC': 1, 'NU_NOTA_MT': 1, 'NU_NOTA_REDACAO': 1
    }

    cursos = collection.find({},projecao)

    df_analise = pd.DataFrame(list(cursos))

    if df_analise.empty:
        return pd.Series(dtype=float)
    
    colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    df_analise = df_analise.dropna(subset=colunas_notas).copy()

    df_analise['NOTA_MEDIA'] = df_analise[colunas_notas].mean(axis=1)
    
    if ano == 2013:
        mapa_escola = {1: 'Pública', 2: 'Privada'}
    else:
        mapa_escola = {2: 'Pública', 3: 'Privada'}
        
    media_por_escola = df_analise.groupby('TP_ESCOLA')['NOTA_MEDIA'].mean()
    media_por_escola.index = media_por_escola.index.map(mapa_escola)
    media_por_escola = media_por_escola.dropna()
    
    return media_por_escola

print('\nProcessando dados, Aguarde.\n')

media_2023 = processar_dados_enem('enem_2023', ano=2023)
media_2013 = processar_dados_enem('enem_2013', ano=2013)

df_comparativo = pd.DataFrame({'2013': media_2013, '2023': media_2023})
df_comparativo = df_comparativo.reindex(['Privada', 'Pública'])
print("\nTabela comparativa de desempenho (Pública vs. Privada):")
print(df_comparativo)

tipos_escola = df_comparativo.index
x = np.arange(len(tipos_escola))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 7))
barras_2013 = ax.bar(x - width/2, df_comparativo['2013'], width, label='2013')
barras_2023 = ax.bar(x + width/2, df_comparativo['2023'], width, label='2023')

ax.set_ylabel('Nota Média Geral')
ax.set_title('Comparativo de Desempenho no ENEM por Tipo de Escola (2013 vs. 2023) (Via MongoDB)')
ax.set_xticks(x)
ax.set_xticklabels(tipos_escola)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

for barra in ax.patches:
    ax.annotate(f'{barra.get_height():.2f}',
                (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                ha='center', va='center',
                xytext=(0, 9),
                textcoords='offset points')

fig.tight_layout()
plt.show()