print('Verificando dependencias...')

import requests
from datetime import datetime, timedelta
import time
import os
import platform
import pyodbc
from dotenv import load_dotenv, dotenv_values



# Carregando variaveis de ambiente
load_dotenv()


# conexao com o banco de dados
veiculosNaoLocalizados = []


def conexaoDb(driver=os.getenv("DRIVER"), server=os.getenv("SERVER"), database=os.getenv("DATABASE"), username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")):
    try:
        # String de conexão formatada corretamente
        conn = pyodbc.connect(f'DRIVER={driver};'
                              f'SERVER={server};'
                              f'DATABASE={database};'
                              f'UID={username};'
                              f'PWD={password}')
        print("Conexão bem-sucedida!")
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)

conexaoDb()



# URL -  EndPoint buscar todos os veiculos
def buscarTodosVeiculosAPI():
    urlListaVeiculos = f"https://ws.fulltrack2.com/vehicles/all/apiKey/{os.getenv('APIKEY')}/secretKey/{os.getenv('SECRETKEY')}"

    listaVeiculos = requests.get(urlListaVeiculos);

    listaVeiculosJson = listaVeiculos.json();

    listaVeiculosIdPlaca = [];

    for item in listaVeiculosJson["data"]:
        listaVeiculosIdPlaca.append({
        "veiculoId": item.get("ras_vei_id", ""),
        "placa": item.get("ras_vei_placa", ""),
        "descricao" : item.get("ras_vei_veiculo"),
        "ano_fabricacao" : item.get("ras_vei_ano"),
        "modelo" : item.get("ras_vei_modelo"),
    })
    
    return listaVeiculosIdPlaca
# URL -  EndPoint buscar todos os motoristas
def buscarTodosCondutoresAPI():
    # URL - EndPoint buscar todos os motoristas
    url = "https://ws.fulltrack2.com/drivers?client=457867"

    payload = {'apiKey': os.getenv("APIKEY"),
    'secretKey': os.getenv("SECRETEKEY")}
    files=[

    ]
    headers = {
    'apiKey': os.getenv("APIKEY"),
    'secretKey': os.getenv("SECRETKEY")
    }

    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        return response.json()  
    else:
        return print("Erro ao buscar motoristas")

def selecionaTodosIdCondutoresDb():
    try: 
        conexao = conexaoDb()
        cursor = conexao.cursor()
        query = """select id from dCondutores_R"""

        cursor.execute(query)

        idTodosCondutores = cursor.fetchall()
        return idTodosCondutores
    
    except Exception as e:
        print(f"Error, {e}") 
def selecionaTodosIdVeiculosDb():
    try: 
        conexao = conexaoDb()
        cursor = conexao.cursor()
        query = """select id from dVeiculos_R"""

        cursor.execute(query)

        idTodosCondutores = cursor.fetchall()
        return idTodosCondutores
    
    except Exception as e:
        print(f"Error, {e}") 

def insertVeiculoDb(idVeiculo, placaVeiculo, descricao, ano_fabricacao, modelo):
    try:
        conexao = conexaoDb()
        cursor = conexao.cursor()

        query_insert = """
        INSERT INTO dVeiculos_R (id, placa, descricao, ano_fabricacao, modelo) 
        VALUES (?, ?, ?, ?, ?);
        """
        
        cursor.execute(query_insert, (idVeiculo, placaVeiculo, descricao, ano_fabricacao, modelo))

        conexao.commit()
        print(f"Veículo {placaVeiculo} (ID: {idVeiculo}) inserido com sucesso.")

    except Exception as e:
        print(f"Erro ao inserir o veículo {placaVeiculo} no banco: {e}")
    finally:
        cursor.close()
        conexao.close()

def insertCondutorDb(idCondutor, nomeCondutor):
    try:
        conexao = conexaoDb()
        cursor = conexao.cursor()

        query = """INSERT INTO dCondutores_R  (id, nome) VALUES (?, ?);"""

        cursor.execute(query, (idCondutor, nomeCondutor))

        print(f"Condutor com nome {nomeCondutor} (ID: {idCondutor}) foi inserido com sucesso.")

        conexao.commit()

    except Exception as e:
        print(f"Error ao inserir o condutor {nomeCondutor} no banco: {e}")
    finally:
        cursor.close()
        conexao.close()

def seExitirVeiculoNovoAdicionaDb():
    listaTodosVeiculosJsonDb = {item[0] for item in listaIdTodosVeiculosDb}
    
    dictTodosVeiculosAPI = {
        int(item["veiculoId"]): item for item in listaTodosVeiculosAPI
    }

    listaNovosVeiculos = {
        idVeiculo: dados for idVeiculo, dados in dictTodosVeiculosAPI.items() 
        if idVeiculo not in listaTodosVeiculosJsonDb
    }

    if listaNovosVeiculos:
        for idVeiculo, dadosVeiculo in listaNovosVeiculos.items():
            insertVeiculoDb(
                idVeiculo, 
                dadosVeiculo["placa"], 
                dadosVeiculo["descricao"], 
                dadosVeiculo["ano_fabricacao"], 
                dadosVeiculo["modelo"]
            )
def seExitirCondutorNovoAdicionaDb():
    listaTodosCondutoresJsonDb = {item[0] for item in listaIdTodosCondutoresDb}
    
    dictTodosCondutoresAPI = {int(item["ras_mot_id"]): item["ras_mot_nome"] for item in listaTodosCondutoresAPI['data']}

    listaNovosCondutores = {idCondutor: nome for idCondutor, nome in dictTodosCondutoresAPI.items() if idCondutor not in listaTodosCondutoresJsonDb}

    if listaNovosCondutores:
        for idCondutor, nomeCondutor in listaNovosCondutores.items():
            insertCondutorDb(idCondutor, nomeCondutor)


veiculosNaoLocalizados = []

def inserirTodasPosicoes(listaTodosVeiculosAPI, horaInicio, horaFim,quantidadeDeVeiculos):

    for veiculos in listaTodosVeiculosAPI:
        quantidadeDeVeiculos = quantidadeDeVeiculos -1
        
        urlIntervaloPosicao = f"https://ws.fulltrack2.com/events/interval/id/{veiculos['veiculoId']}/begin/{horaInicio}/end/{horaFim}/apiKey/daaaf648667667240bafbd1c1bce713a694ee8b4/secretKey/b4b6aa652445542bf62b49e7f6aa0c9cad06c7e8"
        print(f'Inserindo o veiculo com o Id {veiculos["veiculoId"]}...')
        print(f'Ainda faltam {quantidadeDeVeiculos} para coletar posições...')
        intervaloPosicaoVeiculo = requests.get(urlIntervaloPosicao)

        if intervaloPosicaoVeiculo.status_code == 200:
            data = intervaloPosicaoVeiculo.json()
            try:
                if "data" in data:
                    dadosInsertDb = []
                    horaUltimoRegistro = None  

                    for index, item in enumerate(data["data"]):
                        dataInicio = datetime.strptime(item["ras_eve_data_enviado"], "%d/%m/%Y %H:%M:%S")
                        dataAtualBrasil = dataInicio - timedelta(hours=3)  

                        if index == 0:  
                            
                            dadosInsertDb.append((
                                item.get("ras_mot_id", ""),  
                                item.get("ras_vei_id", ""),  
                                item.get("ras_eve_latitude", ""), 
                                item.get("ras_eve_longitude", ""),
                                dataAtualBrasil.strftime("%d/%m/%Y %H:%M:%S"),
                            ))
                            horaUltimoRegistro = dataAtualBrasil  

                        elif horaUltimoRegistro and dataAtualBrasil >= horaUltimoRegistro + timedelta(minutes=20):
                            
                            dadosInsertDb.append((
                                item.get("ras_mot_id", ""),  
                                item.get("ras_vei_id", ""),  
                                item.get("ras_eve_latitude", ""), 
                                item.get("ras_eve_longitude", ""),
                                dataAtualBrasil.strftime("%d/%m/%Y %H:%M:%S"),
                            ))
                            horaUltimoRegistro = dataAtualBrasil  

                    if dadosInsertDb:  
                        query = """
                        INSERT INTO fPosicao_R (condutor_id, veiculo_id, latitude, longitude, data_localizacao) 
                        VALUES (?, ?, ?, ?, ?)
                        """

                        conexao = conexaoDb()    
                        cursor = conexao.cursor()

                        cursor.executemany(query, dadosInsertDb) 

                        conexao.commit()
                        print('Localização foi adicionada ao banco de dados')

                    else:
                        print(f'Nenhuma localização válida para o veículo {veiculos["veiculo_id"]}.')

                else:
                    veiculosNaoLocalizados.append(veiculos['veiculoId'])
                    print(f'Veículo não localizado')

            except Exception as e:
                print(f'Erro ao inserir dados no banco de dados: {e}')
                print({veiculos['veiculoId']})

        else:
            print(f"Erro na requisição: {intervaloPosicaoVeiculo.status_code}")


def limparTerminal():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def conversorHoraOnixFim():
    data_hora = datetime.now()

    timestamp = int(data_hora.timestamp())
    return timestamp
def conversorHoraOnixInicio():
    data_hora = datetime.now() - timedelta(minutes=30)

    timestamp = int(data_hora.timestamp())
    return timestamp


def temporizador(tempo):
    horaFinal = datetime.now() + timedelta(seconds=tempo)
    while tempo > 0:
        minutos = tempo // 60
        segundos = tempo % 60
        print(f"\rTempo restante: {minutos:02}:{segundos:02} | Termina às: {horaFinal.strftime('%H:%M:%S')}", end="")
        time.sleep(1)
        tempo -= 1


while True:
    try:
        print('Aplication running...')
        listaTodosCondutoresAPI = buscarTodosCondutoresAPI();
        listaTodosVeiculosAPI = buscarTodosVeiculosAPI();
        listaIdTodosCondutoresDb = selecionaTodosIdCondutoresDb();
        listaIdTodosVeiculosDb = selecionaTodosIdVeiculosDb();

        seExitirVeiculoNovoAdicionaDb();
        seExitirCondutorNovoAdicionaDb();

        horaInicio = conversorHoraOnixInicio();
        horaFim = conversorHoraOnixFim();
        quantidadeDeVeiculos = len(listaTodosVeiculosAPI)
        inserirTodasPosicoes(listaTodosVeiculosAPI,horaInicio, horaFim, quantidadeDeVeiculos)
        limparTerminal()
        print('Aplication running...')
        print('\n')
        print('Id Veiculos não localizados nesse periodo de tempo')
        print(veiculosNaoLocalizados)
        print('Agurdando tempo de espera...')
        temporizador(1800) #30Min
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário. Finalizando...")
        break
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        time.sleep(30)
