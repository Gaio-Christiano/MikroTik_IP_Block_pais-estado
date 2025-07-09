import re
import requests
import pandas as pd
from time import sleep
from datetime import datetime
from xlwt import Workbook

# Caminho do arquivo exportado do Mikrotik
file_path = "portascan-list.txt"

# Expressão regular para extrair informações relevantes (IP, data, hora e timeout)
pattern = r"PORTASCAN\s+([\d\.]+)\s+(\d{4}-\d{2}-\d{2})\s+([\d:]+)\s+([\d\w]+)"

# Lista para armazenar os dados
dados = []

# Ler o arquivo e extrair IPs, data, hora e timeout
with open(file_path, "r") as arquivo:
    for linha in arquivo:
        match = re.search(pattern, linha)
        if match:
            ip = match.group(1)
            data = match.group(2)
            hora = match.group(3)
            timeout = match.group(4)
            dados.append({"IP": ip, "Data": data, "Hora": hora, "Timeout": timeout})

# Função para consultar a API ipwhois.io
def consultar_geolocalizacao(ip):
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Desconhecida"), data.get("country", "Desconhecido")
        else:
            return "Desconhecida", "Desconhecido"
    except Exception as e:
        return "Desconhecida", "Desconhecido"

# Processar IPs
for idx, entrada in enumerate(dados, start=1):
    ip = entrada["IP"]
    print(f"Processando IP {idx}/{len(dados)}: {ip}")
    cidade, pais = consultar_geolocalizacao(ip)
    entrada["Cidade"] = cidade
    entrada["País"] = pais
    sleep(1)  # Evitar limites de requisição

# Criar um DataFrame do pandas
df = pd.DataFrame(dados)

# Nome do arquivo com dia e hora
hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
arquivo_saida = f"Relatorio_Portascan_{hora_atual}.xls"

# Criar o arquivo Excel
wb = Workbook()

# Aba 1: Detalhes
ws1 = wb.add_sheet("Detalhes")
for col, header in enumerate(df.columns):
    ws1.write(0, col, header)
for row, entry in enumerate(df.values, start=1):
    for col, value in enumerate(entry):
        ws1.write(row, col, value)

# Aba 2: Resumo
ws2 = wb.add_sheet("Resumo")
ws2.write(0, 0, "País")
ws2.write(0, 1, "Quantidade")
ws2.write(0, 2, "Estados Únicos")

# Fórmulas automáticas
for i, pais in enumerate(df["País"].unique(), start=1):
    ws2.write(i, 0, pais)
    ws2.write(i, 1, f'=CONT.SE(Detalhes!E:E, A{i+1})')
    ws2.write(i, 2, f'=SOMARPRODUTO((FREQUÊNCIA(SE(Detalhes!E:E=A{i+1}, CORRESP(Detalhes!D:D, Detalhes!D:D, 0)), LIN(Detalhes!D:D)-LIN(Detalhes!D$1)+1)>0)*1)')

# Salvar o arquivo
wb.save(arquivo_saida)
print(f"Arquivo salvo em: {arquivo_saida}")
