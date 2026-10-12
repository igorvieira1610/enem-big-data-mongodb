import pandas as pd
from pymongo import MongoClient
import os
import time


PASTA_DADOS = r'C:\Users\igor\Downloads\trab big data\dados'

client = MongoClient('mongodb://localhost:27017/')
db = client['enem_db']

def importar_csv_para_mongo(nome_arquivo_csv, nome_colecao):
    caminho_completo = os.path.join(PASTA_DADOS, nome_arquivo_csv)
    
    print("\nProcessando dados, Aguarde.\n")
    
    start_time = time.time()
    
    if not os.path.exists(caminho_completo):
        print(f"\n[ERRO] O arquivo '{nome_arquivo_csv}' não foi encontrado na pasta!")
        print(f"Confira se o nome está correto em: {PASTA_DADOS}")
        return

    if nome_colecao in db.list_collection_names():
        print(f"Limpando dados antigos da coleção '{nome_colecao}'...")
        db[nome_colecao].drop()

    try:
        chunks = pd.read_csv(
            caminho_completo,
            sep=';',
            encoding='latin-1',
            chunksize=10000,
            low_memory=False
        )
        
        collection = db[nome_colecao]
        total_linhas = 0
        
        print("Começando a processar... (isso pode demorar uns minutos)")
        
        for i, chunk in enumerate(chunks):
            dados = chunk.to_dict('records')

            collection.insert_many(dados)
            
            total_linhas += len(dados)

            print(f"Lotes processados: {i+1} | Total de linhas: {total_linhas:,}".replace(',', '.'), end='\r')
        
        tempo_total = (time.time() - start_time) / 60
        print(f"\n\nSUCESSO! Arquivo '{nome_arquivo_csv}' importado.")
        print(f"Total na coleção '{nome_colecao}': {total_linhas} registros.")
        print(f"Tempo levado: {tempo_total:.2f} minutos.")
        
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Ocorreu um problema: {e}")

if __name__ == "__main__":
    importar_csv_para_mongo('MICRODADOS_ENEM_2013.csv', 'enem_2013')
    importar_csv_para_mongo('MICRODADOS_ENEM_2023.csv', 'enem_2023')
    
    print("\n" + "="*50)
    print("PROCESSO FINALIZADO! VERIFIQUE O MONGODB COMPASS.")