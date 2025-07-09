import re
import requests
import pandas as pd
from time import sleep
from datetime import datetime

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

# Criar a contagem por país e estados
resumo = (
    df.groupby("País")
    .agg(
        Quantidade=("País", "size"),
        Estados_Uniquos=("Cidade", lambda x: len(set(x)))
    )
    .reset_index()
)

# Nome do arquivo com dia e hora
hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
arquivo_saida = f"Relatorio_Portascan_{hora_atual}.xls"

# Salvar como Excel com a aba adicional
with pd.ExcelWriter(arquivo_saida, engine="xlwt") as writer:
    df.to_excel(writer, sheet_name="Detalhes", index=False)
    resumo.to_excel(writer, sheet_name="Resumo", index=False)

print(f"Arquivo salvo em: {arquivo_saida}")
