
import pandas as pd
import requests
import time

API_URL = "https://api.opentopodata.org/v1/srtm90m"

def get_elevation(lat, lon):
    url = f"{API_URL}?locations={lat},{lon}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data["results"][0]["elevation"]
        except (KeyError, IndexError):
            return None
    else:
        return None

def process_csv(input_csv, output_csv, delay=1):
    df = pd.read_csv(input_csv)
    if not {'latitude', 'longitude'}.issubset(df.columns):
        raise ValueError("O arquivo CSV precisa conter as colunas 'latitude' e 'longitude'.")

    print("Consultando elevações...")
    elevations = []
    for index, row in df.iterrows():
        elevation = get_elevation(row['latitude'], row['longitude'])
        elevations.append(elevation)
        print(f"{index+1}/{len(df)}: ({row['latitude']}, {row['longitude']}) -> {elevation} m")
        time.sleep(delay)  # Espera para evitar limite da API

    df['elevation'] = elevations
    df.to_csv(output_csv, index=False)
    print(f"Arquivo salvo como: {output_csv}")

if __name__ == "__main__":
    input_csv = "coordenadas.csv"
    output_csv = "coordenadas_com_elevacao.csv"
    process_csv(input_csv, output_csv)
