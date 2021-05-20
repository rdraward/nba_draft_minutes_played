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
  p = row['PLAYER']
  print('processing: ' + p)

  # fix encoding issue from bballref table scrape
  # č = Ä‡, but is coming in as just Ä, which is invalid
  try:
    player = p.encode('cp1252').decode()
  except:
    print('encoding error ' + p)
    
    index = p.find('Ä')
    while index > -1 and index <= len(p):
      try:
        s = 'Ä' + p[index+1]
        s.encode('cp1252').decode()
        index += 1
      except:
        p = p[:index + 1] + '‡' + p[index + 1:]

      index = p.find('Ä', index)

    player = p.encode('cp1252', 'ignore').decode()
    print('encoding error fixed: ' + player)

  try:
    player_df = get_stats(player, stat_type='TOTALS', playoffs=True, career=True, ask_matches=False)
    if not player_df.empty:
      return player_df['MP'].sum()
  except (ValueError, IndexError):
    return 0
  except:
    print('api error ' + player)

  return 0

def add_regression(df, col_name, regression_degree, result_col_name, ax):
  d = np.polyfit(df.index, df[col_name], regression_degree)
  f = np.poly1d(d)
  df.insert(2, result_col_name, f(df.index))

  ax.plot(df['index'], df[result_col_name], color='red', label="Regression")

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

  df.to_csv(r'raw_results/draft_year/{0}_raw.csv'.format(year), header=None, index=None, sep=',', mode='a')

  # only use relevant columns
  df = df[['PICK','TOTALS_MP', 'PLAYOFF_MP']]
  df['PICK'] = df['PICK'].astype(int)
  df['TOTALS_MP'] = pd.to_numeric(df['TOTALS_MP'], 'coerce').fillna(0).astype(int)

  if sort_by_minutes:
    df.sort_values(by=['TOTALS_MP'], inplace=True, ascending=False)
    df.reset_index(inplace=True, drop=True)

  df.to_csv(r'raw_results/draft_year/{0}.csv'.format(year), header=None, index=None, sep=',', mode='a')

  dfs.append(df)

# get average career minutes played
df = pd.concat(dfs).groupby(level=0).agg({'TOTALS_MP': ['mean', q10, q90], 'PLAYOFF_MP': ['mean', q10, q90] })

# flatten columns
df.columns = ['_'.join(x) if x[0] != '' else x[1] for x in df.columns]
df.reset_index(inplace=True)

# group picks by every pick_group_num picks
if group_x_picks:
  df = df.groupby(df[['TOTALS_MP_mean']].index // group_x_picks).mean()

# write to file
if raw_data_file_name:
  df.to_csv(r'raw_results/{0}.csv'.format(raw_data_file_name), header=None, index=None, sep=' ', mode='a')

# build plots
fig, (ax_mp, ax_pmp) = plt.subplots(2)

ax_mp.scatter(df['index'], df['TOTALS_MP_mean'], label='Avg Career Min Played', s=20)
ax_mp.fill_between(df['index'], df['TOTALS_MP_q10'], df['TOTALS_MP_q90'], interpolate=True, color='lightgrey', alpha=0.5, label='10-90% Confidence')
ax_pmp.scatter(df['index'], df['PLAYOFF_MP_mean'], label='Avg Playoff Min Played', s=20)
ax_pmp.fill_between(df['index'], df['PLAYOFF_MP_q10'], df['PLAYOFF_MP_q90'], interpolate=True, color='lavender', alpha=0.5, label='10-90% Playoff Confidence')


# regression
if regression_degree > 0:
  d = np.polyfit(df.index, df['TOTALS_MP_mean'], regression_degree)
  f = np.poly1d(d)
  df.insert(2, 'REGRESSION', f(df.index))

  ax_mp.plot(df['index'], df['REGRESSION'], color='red', label="Regression")

  add_regression(df, 'PLAYOFF_MP_mean', regression_degree, 'PLAYOFF_REGRESSION', ax_pmp)

# set axis limits, labels
ax_mp.set(title="Total", xlabel="Pick #", ylabel="Minutes played")
ax_mp.set_xlim(left=0, right=60)
ax_pmp.set(title="Playoff", xlabel="Pick #", ylabel="Minutes played")
ax_pmp.set_xlim(left=0, right=60)

# chart title
title = '{0} - {1}'.format(min_year, max_year)
if regression_degree > 0:
  regression_title = 'polynomial' if regression_degree > 1 else 'linear'
  title += ' w. {0} regression'.format(regression_title)
if sort_by_minutes:
  title += ' sorted by minutes played'
plt.suptitle(title)

ax_mp.legend()
ax_pmp.legend()

plt.tight_layout()
plt.show()