import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']

def calcular_medias_geograficas(enem_db, ano):
    collection = db[enem_db]
    
    projecao = {
        '_id': 0,
        'SG_UF_PROVA': 1,
        'NU_NOTA_CN': 1, 'NU_NOTA_CH': 1, 'NU_NOTA_LC': 1, 'NU_NOTA_MT': 1, 'NU_NOTA_REDACAO': 1
    }

    cursor = collection.find({}, projecao)
    df_completo = pd.DataFrame(list(cursor))

    colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    df_completo = df_completo.dropna(subset=colunas_notas).copy()
    df_completo['NOTA_MEDIA'] = df_completo[colunas_notas].mean(axis=1)
    
    mapa_regioes = {
        'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
    }
    df_completo['REGIAO'] = df_completo['SG_UF_PROVA'].map(mapa_regioes)
    
    media_por_estado = df_completo.groupby('SG_UF_PROVA')['NOTA_MEDIA'].mean()
    media_por_regiao = df_completo.groupby('REGIAO')['NOTA_MEDIA'].mean()
    
    print ('\nProcessando dados, Aguarde.\n')
    return media_por_estado, media_por_regiao

media_estado_2023, media_regiao_2023 = calcular_medias_geograficas('enem_2023', 2023)
media_estado_2013, media_regiao_2013 = calcular_medias_geograficas('enem_2013', 2013)

print("\n" + "="*60)
print("RELATÓRIO FINAL DE NOTAS MÉDIAS (2013 vs 2023)")
print("="*60)

df_comp_estado = pd.DataFrame({'2013': media_estado_2013, '2023': media_estado_2023}).sort_values(by='2023', ascending=False)
df_comp_estado = df_comp_estado.fillna(0)
print("\n--- Tabela Comparativa por ESTADO ---")
print(df_comp_estado.to_string())

df_comp_regiao = pd.DataFrame({'2013': media_regiao_2013, '2023': media_regiao_2023}).sort_values(by='2023', ascending=False)
df_comp_regiao = df_comp_regiao.fillna(0)
print("\n--- Tabela Comparativa por REGIÃO ---")
print(df_comp_regiao.to_string())


estados = df_comp_estado.index
x_est = np.arange(len(estados))
width = 0.35

fig1, ax1 = plt.subplots(figsize=(20, 10))
ax1.bar(x_est - width/2, df_comp_estado['2013'], width, label='2013')
ax1.bar(x_est + width/2, df_comp_estado['2023'], width, label='2023')
ax1.set_title('Comparativo de Nota Média no ENEM por Estado (2013 vs. 2023) (Via MongoDB)', fontsize=18)
ax1.set_ylabel('Nota Média Geral')
ax1.set_xticks(x_est)
ax1.set_xticklabels(estados)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)
plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
fig1.tight_layout()
print("Mostrando gráfico por ESTADO. Feche a janela para continuar...")
plt.show()

regioes = df_comp_regiao.index
x_reg = np.arange(len(regioes))
cor_2013 = 'skyblue'
cor_2023 = 'steelblue'

fig2, ax2 = plt.subplots(figsize=(12, 7))
ax2.bar(x_reg - width/2, df_comp_regiao['2013'], width, label='2013', color=cor_2013)
ax2.bar(x_reg + width/2, df_comp_regiao['2023'], width, label='2023', color=cor_2023)
ax2.set_title('Comparativo de Nota Média no ENEM por Região (2013 vs. 2023) (Via MongoDB)', fontsize=18)
ax2.set_ylabel('Nota Média Geral')
ax2.set_xticks(x_reg)
ax2.set_xticklabels(regioes)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)
for barra in ax2.patches:
    ax2.annotate(f'{barra.get_height():.2f}',
                (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                ha='center', va='center', xytext=(0, 9), textcoords='offset points')
fig2.tight_layout()
plt.show()