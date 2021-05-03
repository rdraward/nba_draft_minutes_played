import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from basketball_reference_scraper.drafts import get_draft_class

def q10(x):
    return x.quantile(0.10)

def q90(x):
    return x.quantile(0.90)

# get user input
min_year = int(input("Enter start year (ex. 2000):") or "1989")
max_year = int(input("Enter end year (ex. 2005):") or "2006")
regression_degree = int(input("Enter regression degree (1=linear, 2=poly):") or "1")
raw_data_file_name = input("Enter the name of the raw data file to save:")
group_x_picks = int(input("Enter n number of picks to group:") or False)

# query data
dfs = []
for year in range(min_year, max_year + 1):
  df = get_draft_class(year)

  # only use relevant columns
  df = df[['PICK','TOTALS_MP']]
  df['PICK'] = df['PICK'].astype(int)
  df['TOTALS_MP'] = pd.to_numeric(df['TOTALS_MP'], 'coerce').fillna(0).astype(int)

  dfs.append(df)

# get average career minutes played
df = pd.concat(dfs).groupby('PICK').agg({'TOTALS_MP': ['mean', q10, q90] })

# flatten columns
df.columns = ['_'.join(x) if x[0] != '' else x[1] for x in df.columns]
df.reset_index(inplace=True)

# group picks by every pick_group_num picks
if group_x_picks:
  df = df.groupby(df[['TOTALS_MP_mean']].index // group_x_picks).mean()

# write to file
if raw_data_file_name:
  df.to_csv(r'raw_results/{0}.txt'.format(raw_data_file_name), header=None, index=None, sep=' ', mode='a')

# regression
d = np.polyfit(df['PICK'], df['TOTALS_MP_mean'], regression_degree)
f = np.poly1d(d)
df.insert(2, 'REGRESSION', f(df['PICK']))

# chart title
regression_title = 'polynomial' if regression_degree > 1 else 'linear'
title = '{0} - {1}: {2} regression with confidence band'.format(min_year, max_year, regression_title)

# build plot
ax = df.plot(x='PICK', y='TOTALS_MP_mean', title=title, kind='scatter')
df.plot(x='PICK', y='REGRESSION', color='red', ax=ax, label="Regression")
plt.fill_between(df['PICK'], df['TOTALS_MP_q10'], df['TOTALS_MP_q90'], interpolate=True, color='lightgrey', alpha=0.5, label='10-90% Confidence')
plt.legend()

ax.set_xlim(left=0, right=60)
ax.set_xlabel('Pick #')
ax.set_ylabel('Total Career Minutes Played')

plt.show()