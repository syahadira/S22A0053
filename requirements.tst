import pandas as pd
import requests

url = "https://raw.githubusercontent.com/syahadira/S22A0053/refs/heads/main/arts_faculty_data.csv"
response = requests.get(url)

# Save the content to a local CSV file
with open("arts_faculty_data.csv", "wb") as f:
    f.write(response.content)

# Read the CSV into a pandas DataFrame
arts_faculty_df_from_github = pd.read_csv("arts_faculty_data.csv")

# Display the first 5 rows to verify
display(arts_faculty_df_from_github.head())
