import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from basketball_reference_scraper.drafts import get_draft_class

min_year = 2005
max_year = 2006

def q25(x):
    return x.quantile(0.25)

def q75(x):
    return x.quantile(0.75)

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
df = pd.concat(dfs).groupby('PICK').agg({'TOTALS_MP': ['mean', q25, q75] })

# group picks by every pick_group_num picks
# pick_group_num = 5
# df = df.groupby(df[['TOTALS_MP']].index // pick_group_num).mean()

# flatten columns
df.columns = ['_'.join(x) if x[0] != '' else x[1] for x in df.columns]
df.reset_index(inplace=True)

# write to file
# filename = 'results_{0}_{1}.txt'.format(min_year, max_year)
# df.to_csv(r'raw_results/{0}'.format(filename), header=None, index=None, sep=' ', mode='a')

# regression
regression_degree = 2
d = np.polyfit(df['PICK'], df['TOTALS_MP_mean'], regression_degree)
f = np.poly1d(d)
df.insert(2, 'REGRESSION', f(df['PICK']))

# output chart
regression_title = 'polynomial' if regression_degree > 1 else 'linear'
title = '{0} - {1}: {2} regression'.format(min_year, max_year, regression_title)
ax = df.plot(x='PICK', y='TOTALS_MP_mean', title=title, kind='scatter')
df.plot(x='PICK', y='REGRESSION', color='Red', ax=ax)

ax.set_xlim(left=0, right=60)
ax.set_xlabel('Pick #')
ax.set_ylabel('Total Career Minutes Played')

plt.show()