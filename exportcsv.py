import pandas as pd
from jsonConvert import JsonConvert

def exportDataToCsv(name, csv_name):
    repositories = JsonConvert(name).get()
    df = pd.json_normalize(repositories)
    csvText = df.to_csv().replace("\r", "")
    filename = f"{csv_name}"
    print(f"Export repositories on file {filename}")
    file = open(filename, "w")
    file.write(csvText)
    file.close()
    print("Finished export")