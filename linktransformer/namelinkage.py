import linktransformer as lt 
import pandas as pd
import os

def main():
  names_df = pd.read_csv("applicant_names.csv")
  print("read in file...")
  # names_df.sample(1000)

  # names_df.head(10)

  # df_self_matched = lt.merge(names_df, names_df, 
  #                         merge_type='1:m',  # One-to-many merge
  #                         on="applicant",   # Column to match on
  #                         model="sentence-transformers/all-MiniLM-L6-v2")

  df_dedup = lt.dedup_rows(
        names_df,                       # your one list of names
        on="applicant",         # or whatever field(s) hold the names
        model="dell-research-harvard/lt-wikidata-comp-en",
        cluster_params={"threshold": 0.3}  # tweak strictness
  )

  print(df_dedup.head(10))
  df_dedup.to_csv("self_matched.csv", index=False)

if __name__ == "__main__":
  main()