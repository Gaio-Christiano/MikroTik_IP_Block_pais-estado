import re
import requests
import pandas as pd
from time import sleep
from datetime import datetime
from xlwt import Workbook

# Caminho do arquivo exportado
file_path = "portascan-list.txt"

# Regex para capturar dados
pattern = r"PORTASCAN\s+([\d\.]+)\s+(\d{4}-\d{2}-\d{2})\s+([\d:]+)\s+([\d\w]+)"
dados = []

# Ler o arquivo
with open(file_path, "r") as arquivo:
    for linha in arquivo:
        match = re.search(pattern, linha)
        if match:
            ip = match.group(1)
            data = match.group(2)
            hora = match.group(3)
            timeout = match.group(4)
            dados.append({"IP": ip, "Data": data, "Hora": hora, "Timeout": timeout})

# Consultar API para geolocalização
def consultar_geolocalizacao(ip):
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Desconhecida"), data.get("country", "Desconhecido")
        else:
            return "Desconhecida", "Desconhecido"
    except:
        return "Desconhecida", "Desconhecido"

# Processar IPs
for idx, entrada in enumerate(dados, start=1):
    ip = entrada["IP"]
    print(f"Processando IP {idx}/{len(dados)}: {ip}")
    cidade, pais = consultar_geolocalizacao(ip)
    entrada["Cidade"] = cidade
    entrada["País"] = pais
    sleep(1)

# Criar planilha Excel
wb = Workbook()

# Primeira aba: Detalhes
ws_detalhes = wb.add_sheet("Detalhes")
headers = ["IP", "Data", "Hora", "Timeout", "Cidade", "País"]
for col, header in enumerate(headers):
    ws_detalhes.write(0, col, header)

for row, dado in enumerate(dados, start=1):
    ws_detalhes.write(row, 0, dado["IP"])
    ws_detalhes.write(row, 1, dado["Data"])
    ws_detalhes.write(row, 2, dado["Hora"])
    ws_detalhes.write(row, 3, dado["Timeout"])
    ws_detalhes.write(row, 4, dado["Cidade"])
    ws_detalhes.write(row, 5, dado["País"])

# Segunda aba: Resumo
ws_resumo = wb.add_sheet("Resumo")
ws_resumo.write(0, 0, "País")
ws_resumo.write(0, 1, "Quantidade")
ws_resumo.write(0, 2, "Estados Únicos")

# Inserir países únicos e fórmulas
paises_unicos = list(set(d["País"] for d in dados))
for row, pais in enumerate(sorted(paises_unicos), start=1):
    ws_resumo.write(row, 0, pais)
    ws_resumo.write(row, 1, f'=CONT.SE(Detalhes!F:F, A{row + 1})')
    ws_resumo.write(
        row,
        2,
        f'=SOMARPRODUTO((FREQUÊNCIA(SE(Detalhes!F:F=A{row + 1}, CORRESP(Detalhes!E:E, Detalhes!E:E, 0)), LIN(Detalhes!E:E)-LIN(Detalhes!E$1)+1)>0)*1)'
    )

# Salvar arquivo
hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
arquivo_saida = f"Relatorio_Portascan_{hora_atual}.xls"
wb.save(arquivo_saida)
print(f"Arquivo salvo como: {arquivo_saida}")
