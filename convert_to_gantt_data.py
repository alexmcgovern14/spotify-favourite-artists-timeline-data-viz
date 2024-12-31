import pandas as pd

# Path to input CSV
input_csv = "all_artists_albums.csv"

# Path to output CSV
output_csv = "gantt_chart_data_format.csv"

# Read the input data
df = pd.read_csv(input_csv)

# Clean column names by stripping any leading/trailing spaces
df.columns = df.columns.str.strip()

# Print the column names to debug
print("Columns in the CSV:", df.columns)

# Ensure required columns are present
required_columns = ["artist_name", "release_year", "artist_index"]
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"The CSV file must contain the following columns: {required_columns}")

# Convert release_year to numeric (if not already) and convert to integers
df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce').fillna(0).astype(int)

# Drop rows with missing or invalid release years
df = df.dropna(subset=['release_year'])

# Group by artist and calculate the start and end years
artist_gantt = df.groupby('artist_name').agg(
    artist_index=('artist_index', 'first'),
    start_year=('release_year', 'min'),
    end_year=('release_year', 'max')
).reset_index()

# Convert start_year and end_year to strings in 'YYYY' format
artist_gantt['start_year'] = artist_gantt['start_year'].apply(lambda x: str(int(x)))
artist_gantt['end_year'] = artist_gantt['end_year'].apply(lambda x: str(int(x)))

# Calculate the duration (end_year - start_year)
artist_gantt['duration'] = (artist_gantt['end_year'].astype(int) - artist_gantt['start_year'].astype(int)).astype(int)

# Save to a new CSV for Looker Studio
artist_gantt.to_csv(output_csv, index=False)

print(f"Gantt chart data saved to: {output_csv}")
