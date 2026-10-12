import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']

print("\nProcessando dados, Aguarde.\n")

def processar_dados_por_lingua(enem_db, ano):
    collection = db[enem_db]
    
    projecao = {
        '_id': 0,
        'TP_LINGUA': 1,
        'NU_NOTA_CN': 1, 'NU_NOTA_CH': 1, 'NU_NOTA_LC': 1, 'NU_NOTA_MT': 1, 'NU_NOTA_REDACAO': 1
    }

    cursor = collection.find({}, projecao)
    df_completo = pd.DataFrame(list(cursor))
    
    colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    df_analise = df_completo.dropna(subset=colunas_notas).copy()
    df_analise['NOTA_MEDIA'] = df_analise[colunas_notas].mean(axis=1)
    
    media_por_lingua = df_analise.groupby('TP_LINGUA')['NOTA_MEDIA'].mean()
    
    mapa_lingua = {0: 'Inglês', 1: 'Espanhol'}
    media_por_lingua.index = media_por_lingua.index.map(mapa_lingua)
    
    return media_por_lingua

media_lingua_2023 = processar_dados_por_lingua('enem_2023', 2023)
media_lingua_2013 = processar_dados_por_lingua('enem_2013', 2013)

df_comparativo = pd.DataFrame({'2013': media_lingua_2013, '2023': media_lingua_2013}) # Corrigido para media_lingua_2023
df_comparativo = pd.DataFrame({'2013': media_lingua_2013, '2023': media_lingua_2023})
print("\nTabela comparativa de desempenho por escolha de Língua Estrangeira:")
print(df_comparativo)

escolhas = df_comparativo.index
x = np.arange(len(escolhas))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 7))
barras_2013 = ax.bar(x - width/2, df_comparativo['2013'], width, label='2013', color='skyblue')
barras_2023 = ax.bar(x + width/2, df_comparativo['2023'], width, label='2023', color='steelblue')

ax.set_ylabel('Nota Média Geral')
ax.set_title('Comparativo de Desempenho no ENEM por Língua Estrangeira (2013 vs. 2023) (Via MongoDB)\n')
ax.set_xticks(x)
ax.set_xticklabels(escolhas)
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