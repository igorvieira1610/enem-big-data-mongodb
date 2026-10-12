import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']
collection = db['enem_2013']

print('\nProcessando dados, Aguarde.\n')

projecao = {'_id': 0, 'TP_PRESENCA_CH': 1, 'TP_PRESENCA_MT': 1}

cursor = collection.find({}, projecao)
df_2013 = pd.DataFrame(list(cursor))


presente_dia1 = (df_2013['TP_PRESENCA_CH'] == 1)
faltou_dia1 = (df_2013['TP_PRESENCA_CH'] == 0)

presente_dia2 = (df_2013['TP_PRESENCA_MT'] == 1)
faltou_dia2 = (df_2013['TP_PRESENCA_MT'] == 0)

presente_ambos_dias = len(df_2013[presente_dia1 & presente_dia2])

presente_d1_faltou_d2 = len(df_2013[presente_dia1 & faltou_dia2])

faltou_ambos_dias = len(df_2013[faltou_dia1 & faltou_dia2])

faltou_d1_presente_d2 = len(df_2013[faltou_dia1 & presente_dia2])

dados_grafico = {
    'Presente em Ambos os Dias': presente_ambos_dias,
    'Presente D1, Faltou D2': presente_d1_faltou_d2,
    'Faltou em Ambos os Dias': faltou_ambos_dias,
    'Faltou D1, Presente D2': faltou_d1_presente_d2
}

series_grafico = pd.Series(dados_grafico).sort_values(ascending=False)

print("\nPerfil de Presença dos Inscritos:")
print(series_grafico)

plt.figure(figsize=(12, 7))

cores = ["#00fd00", "#ff0000", "#ff0095", "#e5ff00"]
barras = plt.bar(series_grafico.index, series_grafico.values, color=cores)

plt.title('Perfil de Presença dos Inscritos no ENEM 2013 (Via MongoDB)', fontsize=16)
plt.ylabel('Quantidade de Inscritos')

for barra in barras:
    altura = barra.get_height()
    plt.text(barra.get_x() + barra.get_width()/2.0, altura, f'{altura:,.0f}'.replace(',', '.'), ha='center', va='bottom', fontsize=10)

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()