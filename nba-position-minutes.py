import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from basketball_reference_scraper.drafts import get_draft_class

min_year = 1989
max_year = 2020

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
df = pd.concat(dfs).groupby('PICK').mean()
df.reset_index(inplace=True)

# write to file
# filename = 'results_{0}_{1}.txt'.format(min_year, max_year)
# df.to_csv(r'raw_results/{0}'.format(filename), header=None, index=None, sep=' ', mode='a')

# regression
regression_degree = 2
d = np.polyfit(df['PICK'], df['TOTALS_MP'], regression_degree)
f = np.poly1d(d)
df.insert(2, 'REGRESSION', f(df['PICK']))

# output chart
regression_title = 'polynomial' if regression_degree > 1 else 'linear'
title = '{0} - {1}: {2} regression'.format(min_year, max_year, regression_title)
ax = df.plot(x='PICK', y='TOTALS_MP', title=title)
ax.set_xlabel('Pick #')
ax.set_ylabel('Total Career Minutes Played')
df.plot(x='PICK', y='REGRESSION', color='Red', ax=ax)

plt.show()