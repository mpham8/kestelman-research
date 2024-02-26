import pandas as pd

#load in files
parcels_df = pd.read_csv("LA_City_overlap_precinct.csv")
vote_share_df = pd.read_excel("LOS_ANGELES_SPC_MUNI-JJJ_11-08-16_by_Precinct_3496-4917.xls")

print(parcels_df.shape)
print(vote_share_df.shape)

#data cleaning
vote_share_df = vote_share_df.iloc[1:]
vote_share_df.columns = vote_share_df.iloc[0]
vote_share_df = vote_share_df.iloc[1:].reset_index(drop=True)

print(vote_share_df.shape)
cols = vote_share_df.columns.to_list()
print(cols)

#calculations
precinct_ls = vote_share_df['PRECINCT'].to_list()
yes_ls = vote_share_df['YES'].to_list()
no_ls = vote_share_df['NO'].to_list()

print(type(precinct_ls[0]))
print(type(yes_ls[0]))

vote_share_dict = {}
for index, precinct in enumerate(precinct_ls):
  yes_vote = yes_ls[index]
  no_vote = no_ls[index]
  
  if precinct not in vote_share_dict:
    vote_share_dict[precinct] = {'yes': yes_vote, 'no': no_vote}
  else:
    vote_share_dict[precinct]['yes'] += yes_vote
    vote_share_dict[precinct]['no'] += no_vote


for precinct, value in vote_share_dict.items():
  if (vote_share_dict[precinct]['yes'] + vote_share_dict[precinct]['no'] == 0):
    vote_share_dict[precinct]['pct'] = 'No Votes'
  else:
    vote_share_dict[precinct]['pct'] = vote_share_dict[precinct]['yes'] / (vote_share_dict[precinct]['yes'] + vote_share_dict[precinct]['no'])

#print(vote_share_dict)

#new clean df
#parcel ID (AIN), precinct number, Measure JJJ vote share
#print(vote_share_df.iat[0,3])
print(parcels_df.columns.to_list())
parcels_df = parcels_df.drop('pct16', axis=1)
print(parcels_df.shape)
precincts_ls = parcels_df['Precinct'].to_list()

vote_pct_ls = []
for index in range(len(precincts_ls)):
  if precincts_ls[index] in vote_share_dict:
    vote_pct_ls.append(vote_share_dict[precincts_ls[index]]['pct'])
  else:
    vote_pct_ls.append('Missing Precinct')

parcels_df['JJJ-vote-pct'] = vote_pct_ls
print(parcels_df.shape)


#export to csv
parcels_df.to_csv("parcel-vote-share.csv", index=False)
