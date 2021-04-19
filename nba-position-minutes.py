import pandas as pd
from basketball_reference_scraper.drafts import get_draft_class

min_year = 1989
max_year = 2020

dfs = []
for year in range(min_year, max_year):
  df = get_draft_class(year)

  df = df[['PICK','TOTALS_MP']]
  df['PICK'] = df['PICK'].astype(int)
  df['TOTALS_MP'] = pd.to_numeric(df['TOTALS_MP'], 'coerce').fillna(0).astype(int)

  dfs.append(df)

df = pd.concat(dfs).groupby('PICK').mean()
filename = 'results_{0}_{1}.txt'.format(min_year, max_year)
df.to_csv(r'raw_results/{0}'.format(filename), header=None, index=None, sep=' ', mode='a')
