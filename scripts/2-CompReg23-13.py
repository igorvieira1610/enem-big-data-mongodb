import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']

mapa_regioes = {
    'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
}

def obter_dados_regiao(nome_colecao):
    collection = db[nome_colecao]

    pipeline = [
        {"$group": {"_id": "$SG_UF_PROVA", "total": {"$sum": 1}}}
    ]
    
    resultado = list(collection.aggregate(pipeline))
    df = pd.DataFrame(resultado)
    
    if df.empty:
        return pd.Series(dtype=int)

    df.columns = ['Estado', 'Inscricoes']

    df['Regiao'] = df['Estado'].map(mapa_regioes)

    return df.groupby('Regiao')['Inscricoes'].sum()

print ("\nProcessando dados, Aguarde. \n")
regiao_2013 = obter_dados_regiao('enem_2013')

regiao_2023 = obter_dados_regiao('enem_2023')

df_comparativo = pd.DataFrame({'2013': regiao_2013, '2023': regiao_2023})
df_comparativo = df_comparativo.fillna(0)
df_comparativo = df_comparativo.sort_values(by='2023', ascending=False)

print("\nTabela comparativa de inscrições por Região:")
print(df_comparativo)

print("\nGerando o gráfico comparativo por região...")

regioes = df_comparativo.index
x = np.arange(len(regioes))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 7))

barras_2013 = ax.bar(x - width/2, df_comparativo['2013'], width, label='2013', color='#0a05ff')
barras_2023 = ax.bar(x + width/2, df_comparativo['2023'], width, label='2023', color='#ff0000')

ax.set_ylabel('Quantidade de Inscrições')
ax.set_title('Comparativo de Inscrições no ENEM por Região: 2013 vs 2023 (Via MongoDB)')
ax.set_xticks(x)
ax.set_xticklabels(regioes)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

for barra in ax.patches:
    altura = barra.get_height()
    if pd.isna(altura): altura = 0
    
    ax.annotate(f"{int(altura):,.0f}".replace(",", "."),
                (barra.get_x() + barra.get_width() / 2, altura),
                ha='center', va='center',
                xytext=(0, 9),
                textcoords='offset points')

fig.tight_layout()
plt.show()