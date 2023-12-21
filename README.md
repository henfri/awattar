This code reads in your meter-data (example: meter_data.csv, Grafana/Influx export) and calculates what you would have paid at awattar, tibber or similar. Note that the input file must be in Wh (Watt Hours) and not in kWh. Also note the formatting of the time/date.

Output:
```
Year-Month: (2023, 5), Consumption: 206.0kWh, Cost: 52.3€, Price: 25.4 ct/kwh
Year-Month: (2023, 6), Consumption: 164.0kWh, Cost: 42.9€, Price: 26.2 ct/kwh
Year-Month: (2023, 7), Consumption: 153.0kWh, Cost: 37.1€, Price: 24.2 ct/kwh
Year-Month: (2023, 8), Consumption: 264.0kWh, Cost: 67.5€, Price: 25.6 ct/kwh
Year-Month: (2023, 9), Consumption: 218.0kWh, Cost: 57.6€, Price: 26.5 ct/kwh
Year-Month: (2023, 10), Consumption: 331.0kWh, Cost: 83.2€, Price: 25.1 ct/kwh
Year-Month: (2023, 11), Consumption: 407.0kWh, Cost: 104.5€, Price: 25.7 ct/kwh
Year-Month: (2023, 12), Consumption: 319.0kWh, Cost: 82.4€, Price: 25.9 ct/kwh

Year: 2023, Consumption: 2061.0kWh, Cost: 527.5€, Price: 25.6 ct/kwh
```

In addition two csv files (Market-Price from awattar api and calculation results) are written.

Usage Edit these variables
```
increment=15.31  # the increment that your provider adds on the Market-Price
factor=1+0.03    # the factor (here 3%) that your provider adds on the Market-Price

meter_csv_filename = 'meter_data.csv'   # your meter data

```
And run the file.
