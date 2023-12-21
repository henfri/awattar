import requests
import csv
from datetime import datetime, timedelta

def get_market_data_old(start_date, end_date):
    # Hier sollte der Code stehen, um die Daten vom API-Endpunkt abzurufen.
    # Der folgende Code ist ein allgemeines Beispiel und muss angepasst werden.
    
    api_url = "https://api.awattar.de/v1/marketdata"
    
    # Formatieren der Datumsangaben in Millisekunden seit dem Unixepoch
    start_timestamp = int((start_date - datetime(1970, 1, 1)).total_seconds()) * 1000
    end_timestamp = int((end_date - datetime(1970, 1, 1)).total_seconds()) * 1000
    
    # Beispiel-Parameter für den API-Aufruf
    params = {
        "start": start_timestamp,
        "end": end_timestamp
    }
    
    # API-Aufruf
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        market_data = response.json()["data"]
        result = [(datetime.utcfromtimestamp(entry["start_timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S'), entry["marketprice"]) for entry in market_data]
        return result
    else:
        # Fehlerbehandlung, falls der API-Aufruf nicht erfolgreich ist
        print(f"Fehler beim API-Aufruf. Statuscode: {response.status_code}")
        return None

def get_market_data(start_date, end_date):
    # Hier sollte der Code stehen, um die Daten vom API-Endpunkt abzurufen.
    # Der folgende Code ist ein allgemeines Beispiel und muss angepasst werden.
    
    api_url = "https://api.awattar.de/v1/marketdata"
    
    # Formatieren der Datumsangaben in Millisekunden seit dem Unixepoch
    start_timestamp = int((start_date - datetime(1970, 1, 1)).total_seconds()) * 1000
    end_timestamp = int((end_date - datetime(1970, 1, 1)).total_seconds()) * 1000
    
    # Beispiel-Parameter für den API-Aufruf
    params = {
        "start": start_timestamp,
        "end": end_timestamp
    }
    
    # API-Aufruf
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        market_data = response.json()["data"]
        result = [(datetime.utcfromtimestamp(entry["start_timestamp"] / 1000), entry["marketprice"]) for entry in market_data]
        return result
    else:
        # Fehlerbehandlung, falls der API-Aufruf nicht erfolgreich ist
        print(f"Fehler beim API-Aufruf. Statuscode: {response.status_code}")
        return None


def write_to_csv(data, csv_filename):
    # Schreibe die Daten in eine CSV-Datei
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Schreibe Header
        writer.writerow(['Zeitpunkt', 'Marktpreis (Eur/MWh)'])
        
        # Schreibe Daten
        writer.writerows(data)




import pandas as pd

def read_meter_data(csv_filename):
    # Lese die Stromzählerdaten aus der CSV-Datei mit Pandas ein
    df = pd.read_csv(csv_filename, sep=',', skiprows=0, parse_dates=["Time"])

    # Umbenenne die Spalte für bessere Verwendung
    df.rename(columns={df.columns[1]: "Value"}, inplace=True)
    df.rename(columns={df.columns[0]: "Time"}, inplace=True)



    # Wandele die Daten in ein Listentupel um, und konvertiere die Zeitangaben zu datetime-Objekten
    meter_data = [(row["Time"].to_pydatetime(), row["Value"]) for _, row in df.iterrows()]

    return meter_data

def calculate_consumption(meter_data, start_date, end_date):
    # Berechne den verbrauchten Strom zwischen zwei Zeilen in der Liste
    consumption_data = []
    for i in range(len(meter_data)-1):
        current_date, current_reading = meter_data[i]
        next_date, next_reading = meter_data[i+1]

        if start_date <= current_date <= end_date:
            consumption = next_reading - current_reading
            if consumption < 0: consumption=0
            consumption_data.append((current_date, consumption))
        #else:
        #    print("error")

    return consumption_data



def check_matching_dates(meter_data, market_data):
    # Überprüfe, ob für jede Zeile in einer CSV-Datei eine Zeile in der anderen CSV-Datei vorhanden ist
    meter_dates = set(date for date, _ in meter_data)
    market_dates = set(date for date, _ in market_data)

    missing_in_meter = meter_dates - market_dates
    missing_in_market = market_dates - meter_dates

    #if missing_in_meter:
    #    print(f"Fehlende Daten im Zählerdatensatz für die folgenden Zeitpunkte: {missing_in_meter}")
    if missing_in_market:
        print(f"Fehlende Daten im Marktdatensatz für die folgenden Zeitpunkte: {missing_in_market}")

import csv
from datetime import datetime

def write_consumption_cost_to_csv(meter_data, consumption_data, cost_data, csv_filename):
    # Schreibe die Daten in eine CSV-Datei und erstelle eine Liste mit den geschriebenen Daten
    written_data = []

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Schreibe Header
        writer.writerow(['Datum', 'Zählerstand', 'Verbrauch', 'Preis', 'Kosten'])

        # Schreibe Daten
        for (meter_date, meter_reading) in meter_data:
            # Finde die Kosten- und Preisdaten für das aktuelle Datum
            data_entry = next((entry for entry in cost_data if entry['Datum'] == meter_date), None)

            # Extrahiere die relevanten Werte
            consumption_entry = next((entry[1] for entry in consumption_data if entry[0] == meter_date), None)

            cost_entry = data_entry['Kosten'] if data_entry else None
            price_entry = data_entry['Preis'] if data_entry else None

            # Schreibe die Zeile
            row = [meter_date.strftime('%Y-%m-%d %H:%M:%S'), meter_reading, consumption_entry, price_entry, cost_entry]
            writer.writerow(row)
            written_data.append({'Datum': meter_date, 'Zählerstand': meter_reading, 'Verbrauch': consumption_entry, 'Preis': price_entry, 'Kosten': cost_entry})

    return written_data

def calculate_cost(consumption_data, market_data, increment, factor):
    # Multipliziere den Verbrauch mit den jeweiligen Marktpreisen
    cost_data = []

    # Erstelle ein Dictionary, um die Datumsangaben im market_data-Datensatz zu indizieren
    market_data_index = {date.strftime('%Y-%m-%d %H:%M:%S'): price for date, price in market_data}
    
    for date, consumption in consumption_data:
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Überprüfe, ob das Datum im market_data vorhanden ist
        if date_str in market_data_index:
            market_price = market_data_index[date_str]
            market_price_ct_per_kwh= market_price*100.0 / 1000.0
            price = ( market_price_ct_per_kwh* factor + increment ) / 100 #price in € 
            cost = consumption / 1000 * price
            cost_data.append({'Datum': date, 'Kosten': cost, 'Preis': price})
        else:
            print(f"Fehlender Marktpreis für das Datum {date_str}")

    return cost_data

def sum_consumption_cost_per_day(written_data):
    daily_sum = {}

    for row in written_data:
        date = row['Datum']
        consumption = row['Verbrauch']
        cost = row['Kosten']
        price = row['Preis']

        # Stelle sicher, dass consumption eine Zahl ist
        consumption = float(consumption) if consumption is not None else 0

        if date not in daily_sum:
            daily_sum[date] = {'consumption': 0, 'cost': 0, 'price': 0}

        daily_sum[date]['consumption'] += consumption
        if cost is not None: daily_sum[date]['cost'] += cost
        if cost is not None and consumption > 0: 
            daily_sum[date]['price'] += price

    # Berechne den Preis (Kosten pro Verbrauchseinheit) und füge ihn zu daily_sum hinzu
    for date, values in daily_sum.copy().items():
        if values['consumption']>0:
            daily_sum[date]['price'] = values['cost'] / values['consumption']*1000

    return daily_sum





def sum_consumption_cost_per_month(written_data):
    monthly_sum = {}

    for row in written_data:
        date = row['Datum']
        consumption = row['Verbrauch']
        cost = row['Kosten']
        price = row['Preis']

        # Extrahiere das Jahr und den Monat aus dem Datum
        year_month = (date.year, date.month)

        if year_month not in monthly_sum:
            monthly_sum[year_month] =  {'consumption': 0, 'cost': 0, 'price': 0}

        if consumption is not None: monthly_sum[year_month]['consumption'] += consumption
        if cost is not None: monthly_sum[year_month]['cost'] += cost

    # Berechne den Preis (Kosten pro Verbrauchseinheit) und füge ihn zu daily_sum hinzu
    for year_month, values in monthly_sum.copy().items():
        if values['consumption']>0:
            monthly_sum[year_month]['price'] = values['cost'] / values['consumption']*1000

    return monthly_sum

def sum_consumption_cost_per_year(written_data):
    yearly_sum = {}

    for row in written_data:
        date = row['Datum']
        consumption = row['Verbrauch']
        cost = row['Kosten']
        price = row['Preis']


        # Extrahiere das Jahr aus dem Datum
        year = date.year

        if year not in yearly_sum:
            yearly_sum[year] =  {'consumption': 0, 'cost': 0, 'price': 0}

        if consumption is not None: yearly_sum[year]['consumption'] += consumption
        if cost is not None: yearly_sum[year]['cost'] += cost

    
    # Berechne den Preis (Kosten pro Verbrauchseinheit) und füge ihn zu daily_sum hinzu
    for date, values in yearly_sum.copy().items():
        if values['consumption']>0:
            yearly_sum[year]['price'] = values['cost'] / values['consumption']*1000

    return yearly_sum


increment=15.31
factor=1+0.03

meter_csv_filename = 'zaehlerstand.csv'
market_csv_filename = 'market_data.csv'

meter_data = read_meter_data(meter_csv_filename)

start_date = min(meter_data, key=lambda x: x[0])[0]
end_date = max(meter_data, key=lambda x: x[0])[0]


# Beispielaufruf
start_date = datetime(2023, 5, 1, 0, 0, 0)  # Beispiel: 08.11.2021 00:00:00
end_date = datetime(2023, 12, 18, 1, 0, 0)    # Beispiel: 10.11.2021 00:00:00
market_data = get_market_data(start_date, end_date)

if market_data:
    csv_filename = 'market_data.csv'
    write_to_csv(market_data, csv_filename)

consumption_data = calculate_consumption(meter_data, start_date, end_date)

# Hier müsstest du die Funktion get_market_data aus dem vorherigen Beispiel einfügen
market_data = get_market_data(start_date, end_date)

cost_data = calculate_cost(consumption_data, market_data, increment,factor)


check_matching_dates(meter_data, market_data)

# Schreibe die Daten in eine CSV-Datei
result_csv_filename = 'result_data.csv'
data_list=write_consumption_cost_to_csv(meter_data, consumption_data, cost_data, result_csv_filename)

daily_sum = sum_consumption_cost_per_day(data_list)
monthly_sum = sum_consumption_cost_per_month(data_list)
yearly_sum = sum_consumption_cost_per_year(data_list)


# Beispiel: Ausgabe der Summen pro Monat
for year_month, values in monthly_sum.items():
    print(f'Year-Month: {year_month}, Consumption: {round(values["consumption"]/1000.0,0)}kWh, Cost: {round(values["cost"],1)}€, Price: {round(values["price"]*100,1)} ct/kwh')

# Beispiel: Ausgabe der Summen pro Jahr
for year, values in yearly_sum.items():
    print(f'Year: {year}, Consumption: {round(values["consumption"]/1000.0,0)}kWh, Cost: {round(values["cost"],1)}€, Price: {round(values["price"]*100,1)} ct/kwh')
