import os
import requests
import pandas as pd

# CONFIGURATION
# We fetch the token from the "Environment" (GitHub Secrets)
API_TOKEN = os.environ.get("BANXICO_TOKEN")

if not API_TOKEN:
    raise ValueError("BANXICO_TOKEN not found. Check your GitHub Secrets.")

SERIES_IDS = {
    'SF43936': 'Cetes 28 days',
    'SF43939': 'Cetes 91 days',
    'SF43942': 'Cetes 182 days',
    'SF43945': 'Cetes 364 days',
    'SF43948': 'Cetes 728 days',
    'SF44070': 'Bonos 3 years',
    'SF44073': 'Bonos 5 years',
    'SF44076': 'Bonos 7 years',
    'SF45383': 'Bonos 10 years',
    'SF45384': 'Bonos 20 years',
    'SF61504': 'Bonos 30 years',
    'SF43951': 'Udibonos 3 years',
    'SF43952': 'Udibonos 5 years',
    'SF43954': 'Udibonos 10 years',
    'SF45421': 'Udibonos 20 years',
    'SF45386': 'Udibonos 30 years'
}

BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

def get_banxico_data(series_id, series_name, token):
    url = f"{BASE_URL}/{series_id}/datos"
    headers = {'Bmx-Token': token}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Check integrity
        if 'bmx' not in data or 'series' not in data['bmx']:
            return None
        
        timeseries_data = data['bmx']['series'][0]['datos']
        df = pd.DataFrame(timeseries_data)
        df.rename(columns={'dato': series_name, 'fecha': 'Date'}, inplace=True)
        
        # Format data
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df[series_name] = pd.to_numeric(df[series_name], errors='coerce')
        return df.set_index('Date')
        
    except Exception as e:
        print(f"Error fetching {series_name}: {e}")
        return None

def main():
    print("Starting Banxico Data Pipeline...")
    data_frames = []
    for s_id, s_name in SERIES_IDS.items():
        print(f"Fetching {s_name}...")
        df = get_banxico_data(s_id, s_name, API_TOKEN)
        if df is not None:
            data_frames.append(df)
            
    if data_frames:
        final_df = pd.concat(data_frames, axis=1).sort_index()
        
        # Ensure 'data' folder exists
        os.makedirs('data', exist_ok=True)
        
        # Save
        final_df.to_csv('data/banxico_rates.csv')
        print("Success: Database updated.")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
