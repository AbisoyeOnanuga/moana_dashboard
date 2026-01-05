from data_loader import load_metadata

df = load_metadata("../data/moana_metadata.csv")
print(df.head())
print(df.describe())
print(df['asset_type'].unique())

from processing import apply_filters, get_heaviest, compute_suggestions

df = load_metadata("../data/moana_metadata.csv")

filtered = apply_filters(df, asset_type="main", poly_range=(0, 1_000_000))
print(filtered.head())

print(get_heaviest(df, 5))

print(compute_suggestions(filtered))
