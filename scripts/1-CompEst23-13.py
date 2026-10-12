import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']

def obter_contagem_por_estado(enem_db):
    collection = db[enem_db]

    pipeline = [
        {"$group": {"_id": "$SG_UF_PROVA", "total": {"$sum": 1}}}
    ]
    
    resultado = list(collection.aggregate(pipeline))

    df = pd.DataFrame(resultado)

    if df.empty:
        return pd.Series(dtype=int)

    df = df.set_index('_id')['total']
    return df

print ("\nProcesando dados, Aguarde.\n")
contagem_2013 = obter_contagem_por_estado('enem_2013')
contagem_2023 = obter_contagem_por_estado('enem_2023')

df_comparativo = pd.DataFrame({'2013': contagem_2013, '2023': contagem_2023})
df_comparativo = df_comparativo.fillna(0)
df_comparativo = df_comparativo.sort_values(by='2023', ascending=False)

print("\nTabela comparativa de inscrições por estado:\n")
print(df_comparativo)

estados = df_comparativo.index
x = np.arange(len(estados))
width = 0.35

fig, ax = plt.subplots(figsize=(20, 10))

barras_2013 = ax.bar(x - width/2, df_comparativo['2013'], width, label='2013', color="#0a05ff")
barras_2023 = ax.bar(x + width/2, df_comparativo['2023'], width, label='2023', color="#ff0000")

ax.set_ylabel('Quantidade de Inscrições')
ax.set_title('Comparativo de Inscrições no ENEM por Estado: 2013 vs 2023 (Via MongoDB)')
ax.set_xticks(x)
ax.set_xticklabels(estados)
ax.legend()

plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

print("Gerando gráfico...")
plt.show()