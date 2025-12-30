from data_loader import load_metadata

df = load_metadata("../data/moana_metadata.csv")
print(df.head())
print(df.describe())
print(df['asset_type'].unique())
