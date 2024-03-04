import pandas as pd

crime_df = pd.read_csv("crimedata.csv")

print("Old shape")
print(crime_df.shape)
print(crime_df.info())
print(crime_df.head())

# Check for missing values
print("\nMissing values in the dataset:")
print(crime_df.isnull().sum())

# duplicate rows
crime_df = crime_df.drop_duplicates()

print("New shape")
print(crime_df.shape)
print(crime_df.info())
print(crime_df.head())