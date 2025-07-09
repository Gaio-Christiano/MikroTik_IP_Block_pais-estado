import re
import requests
import pandas as pd
from time import sleep
from datetime import datetime
from xlwt import Workbook

# Dados simulados (apenas para exemplo, substitua pelo processamento real)
dados = [
    {"IP": "202.165.22.33", "Data": "2024-12-16", "Hora": "16:04:30", "Timeout": "2w3d6h48m34s", "Cidade": "Kuala Lumpur", "País": "Malaysia"},
    {"IP": "125.228.50.215", "Data": "2024-12-16", "Hora": "16:07:40", "Timeout": "2w3d6h51m6s", "Cidade": "Taipei", "País": "Taiwan"},
    {"IP": "122.168.123.76", "Data": "2024-12-16", "Hora": "16:08:57", "Timeout": "2w3d6h52m23s", "Cidade": "Bhopal", "País": "India"},
    {"IP": "68.169.247.136", "Data": "2024-12-16", "Hora": "16:12:25", "Timeout": "2w3d6h55m51s", "Cidade": "Dubuque", "País": "United States"},
    {"IP": "65.49.1.19", "Data": "2024-12-16", "Hora": "16:22:50", "Timeout": "2w3d7h6m16s", "Cidade": "San Francisco", "País": "United States"}
]

# Criar a planilha Excel
wb = Workbook()

# Aba "Detalhes"
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

# Aba "Resumo"
ws_resumo = wb.add_sheet("Resumo")
ws_resumo.write(0, 0, "País")
ws_resumo.write(0, 1, "Quantidade")
ws_resumo.write(0, 2, "Estados Únicos")

# Adicionar países únicos e fórmulas
paises_unicos = sorted(set(d["País"] for d in dados))
for row, pais in enumerate(paises_unicos, start=1):
    ws_resumo.write(row, 0, pais)
    # Fórmulas
    ws_resumo.write(row, 1, f'=CONT.SE(Detalhes!F:F, A{row + 1})')  # Quantidade
    ws_resumo.write(
        row,
        2,
        f'=SOMARPRODUTO((FREQUÊNCIA(SE(Detalhes!F:F=A{row + 1}, CORRESP(Detalhes!E:E, Detalhes!E:E, 0)), LIN(Detalhes!E:E)-LIN(Detalhes!E$1)+1)>0)*1)'
    )  # Estados Únicos

# Salvar o arquivo
hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
arquivo_saida = f"Relatorio_Portascan_{hora_atual}.xls"
wb.save(arquivo_saida)
print(f"Arquivo salvo como: {arquivo_saida}")
