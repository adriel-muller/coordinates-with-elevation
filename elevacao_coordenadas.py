import pandas as pd
import requests
import time
import utm  # pip install utm

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

def process_csv(input_csv, output_csv, utm_zone_number=None, northern_hemisphere=True, delay=1):
    df = pd.read_csv(input_csv)
    if not {'Node', 'X-Coord', 'Y-Coord'}.issubset(df.columns):
        raise ValueError("O CSV deve conter as colunas 'Node', 'X-Coord' e 'Y-Coord'.")

    print("Convertendo UTM para latitude/longitude e consultando elevações...")
    results = []

    for index, row in df.iterrows():
        try:
            lat, lon = utm.to_latlon(
                row['X-Coord'], row['Y-Coord'],
                zone_number=utm_zone_number,
                northern=northern_hemisphere
            )
        except Exception as e:
            print(f"Erro ao converter UTM para o ponto {row['Node']}: {e}")
            lat, lon = None, None

        elevation = get_elevation(lat, lon) if lat is not None and lon is not None else None
        results.append({'Node': row['Node'], 'elevacao': elevation})
        print(f"{index+1}/{len(df)}: Node {row['Node']} -> elevação {elevation} m")
        time.sleep(delay)

    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"Arquivo salvo como: {output_csv}")

if __name__ == "__main__":
    input_csv = "coordenadas_utm.csv"
    output_csv = "pontos_com_elevacao.csv"
    # Exemplo: zona 22 (para Rio Grande do Sul), hemisfério sul
    process_csv(input_csv, output_csv, utm_zone_number=22, northern_hemisphere=False)
