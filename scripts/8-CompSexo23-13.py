import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']

def processar_dados_por_sexo(enem_db, ano):
    collection = db[enem_db]

    projecao = {
        '_id': 0,
        'TP_SEXO': 1,
        'NU_NOTA_CN': 1, 'NU_NOTA_CH': 1, 'NU_NOTA_LC': 1, 'NU_NOTA_MT': 1, 'NU_NOTA_REDACAO': 1
    }

    print('\nProcessando dados, Aguarde\n')

    cursor = collection.find({}, projecao)
    df_analise = pd.DataFrame(list(cursor))
    
    colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    df_analise = df_analise.dropna(subset=colunas_notas).copy()
    df_analise['NOTA_MEDIA'] = df_analise[colunas_notas].mean(axis=1)
    
    media_por_sexo = df_analise.groupby('TP_SEXO')['NOTA_MEDIA'].mean()
    
    mapa_sexo = {'M': 'Masculino', 'F': 'Feminino'}
    media_por_sexo.index = media_por_sexo.index.map(mapa_sexo)
    
    return media_por_sexo

media_sexo_2023 = processar_dados_por_sexo('enem_2023', 2023)
media_sexo_2013 = processar_dados_por_sexo('enem_2013', 2013)

df_comparativo = pd.DataFrame({'2013': media_sexo_2013, '2023': media_sexo_2023})
print("\nTabela comparativa de desempenho por Sexo:")
print(df_comparativo)

print("\nGerando gráfico comparativo...")
categorias = df_comparativo.index
x = np.arange(len(categorias))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 7))
barras_2013 = ax.bar(x - width/2, df_comparativo['2013'], width, label='2013', color='lightcoral')
barras_2023 = ax.bar(x + width/2, df_comparativo['2023'], width, label='2023', color='firebrick')

ax.set_ylabel('Nota Média Geral')
ax.set_title('Comparativo de Desempenho no ENEM por Sexo (2013 vs. 2023) (Via MongoDB)', fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(categorias)
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