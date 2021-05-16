import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from basketball_reference_scraper.drafts import get_draft_class
from basketball_reference_scraper.players import get_stats

def q10(x):
    return x.quantile(0.10)

def q90(x):
    return x.quantile(0.90)

def get_playoff_minutes(row):
  try:
    player_df = get_stats(row['PLAYER'], stat_type='TOTALS', playoffs=True, career=True)
    if not player_df.empty:
      return player_df['MP'].sum()
  except (ValueError, IndexError, AttributeError):
    return 0

# get user input
min_year = int(input("Enter start year (ex. 2000): ") or "1989")
max_year = int(input("Enter end year (ex. 2005): ") or "2006")
regression_degree = int(input("Enter regression degree (0=none, 1=linear, 2=poly): ") or "0")
raw_data_file_name = input("Enter the name of the raw data file to save: ")
group_x_picks = int(input("Enter n number of picks to group: ") or False)
sort_by_minutes = input("Sort by career minutes played? (T, F): ").lower() == "t"

# query data
dfs = []
for year in range(min_year, max_year + 1):
  df = get_draft_class(year)

  df['PLAYOFF_MP'] = df.apply(get_playoff_minutes, axis=1)

  # only use relevant columns
  df = df[['PICK','TOTALS_MP', 'PLAYOFF_MP']]
  df['PICK'] = df['PICK'].astype(int)
  df['TOTALS_MP'] = pd.to_numeric(df['TOTALS_MP'], 'coerce').fillna(0).astype(int)

  if sort_by_minutes:
    df.sort_values(by=['TOTALS_MP'], inplace=True, ascending=False)
    df.reset_index(inplace=True, drop=True)

  dfs.append(df)

# get average career minutes played
df = pd.concat(dfs).groupby(level=0).agg({'TOTALS_MP': ['mean', q10, q90] })

# flatten columns
df.columns = ['_'.join(x) if x[0] != '' else x[1] for x in df.columns]
df.reset_index(inplace=True)

# group picks by every pick_group_num picks
if group_x_picks:
  df = df.groupby(df[['TOTALS_MP_mean']].index // group_x_picks).mean()

# write to file
if raw_data_file_name:
  df.to_csv(r'raw_results/{0}.txt'.format(raw_data_file_name), header=None, index=None, sep=' ', mode='a')

# build plot
plt.scatter(df['index'], df['TOTALS_MP_mean'], label='Avg Career Min Played', s=20)
plt.fill_between(df['index'], df['TOTALS_MP_q10'], df['TOTALS_MP_q90'], interpolate=True, color='lightgrey', alpha=0.5, label='10-90% Confidence')
plt.legend()

# regression
if regression_degree > 0:
  d = np.polyfit(df.index, df['TOTALS_MP_mean'], regression_degree)
  f = np.poly1d(d)
  df.insert(2, 'REGRESSION', f(df.index))

  plt.plot(df['index'], df['REGRESSION'], color='red', label="Regression")

# set axis limits, labels
ax = plt.gca()
ax.set_xlim(left=0, right=60)
ax.set_xlabel('Pick #')
ax.set_ylabel('Total Career Minutes Played')

# chart title
title = '{0} - {1}'.format(min_year, max_year)
if regression_degree > 0:
  regression_title = 'polynomial' if regression_degree > 1 else 'linear'
  title += ' w. {0} regression'.format(regression_title)
if sort_by_minutes:
  title += ' sorted by minutes played'
plt.title(title)

plt.show()