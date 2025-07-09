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
data = []

# Ler o arquivo e extrair IPs, data, hora e timeout
with open(file_path, "r") as file:
    for line in file:
        match = re.search(pattern, line)
        if match:
            ip = match.group(1)
            date = match.group(2)
            time = match.group(3)
            timeout = match.group(4)
            data.append({"IP": ip, "Date": date, "Time": time, "Timeout": timeout})

# Função para consultar a API ipwhois.io
def fetch_geolocation(ip):
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Unknown"), data.get("country", "Unknown")
        else:
            return "Unknown", "Unknown"
    except Exception as e:
        return "Unknown", "Unknown"

# Processar IPs
for idx, entry in enumerate(data, start=1):
    ip = entry["IP"]
    print(f"Processando IP {idx}/{len(data)}: {ip}")
    city, country = fetch_geolocation(ip)
    entry["City"] = city
    entry["Country"] = country
    sleep(1)  # Evitar limites de requisição

# Criar um DataFrame do pandas
df = pd.DataFrame(data)

# Criar a contagem por país e estados
country_summary = df.groupby("Country").agg(
    Count=("Country", "size"),
    Unique_States=("City", lambda x: len(x.unique()))
).reset_index()

# Nome do arquivo com dia e hora
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = f"Portascan_Report_{current_time}.xls"

# Salvar como Excel com a aba adicional
with pd.ExcelWriter(output_file, engine="xlwt") as writer:
    df.to_excel(writer, sheet_name="Detalhes", index=False)
    country_summary.to_excel(writer, sheet_name="Resumo", index=False)

print(f"Arquivo salvo em: {output_file}")
