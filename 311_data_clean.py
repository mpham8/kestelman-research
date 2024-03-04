import pandas as pd

calls_df = pd.read_csv("311_2022.csv")


print("Old shape")
print(calls_df.columns)
print(calls_df.shape)
print(calls_df.info())
print(calls_df.head())

# Check for missing values
print("\nMissing values in the dataset:")
print(calls_df.isnull().sum())

#missing location
calls_df = calls_df.dropna(subset=['Latitude'])
calls_df = calls_df.dropna(subset=['Longitude'])

# duplicate rows
calls_df = calls_df.drop_duplicates()

print("New shape")
print(calls_df.shape)
print(calls_df.info())
print(calls_df.head())