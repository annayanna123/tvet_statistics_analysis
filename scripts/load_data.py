import pandas as pd 

df = pd.read_csv(r"C:\Users\Anna May\Downloads\FANRBF\TVET_Stats_Analysis\tvet_statistics_analysis\data\cleaned\cleaned_tvet_data.csv")

# connect to the neon database

conn = sqlite3.connect('neon_database.db')

