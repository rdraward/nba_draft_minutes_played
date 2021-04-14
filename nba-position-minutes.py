import math
from statistics import mean
import pandas as pd
import numpy as np
from basketball_reference_scraper.draft import get_draft_class

min_year = 1990
max_year = 2005

# capture the total minutes played (career) for each draft position
minutes_per_draft_pos = {};

for year in range(min_year, max_year):
  draft_class = get_draft_class(year)

  # iterate over players drafted
  # max of 60, not much overhead
  for index, row in draft_class.iterrows():
    draft_pos = row.PICK.Pk

    if draft_pos == "Pk":
      draft_pos = math.nan
    minutes = row.TOTALS.MP

    if not str(minutes).isnumeric() or math.isnan(float(minutes)):
      minutes = 0

    if not math.isnan(float(draft_pos)):
      pos = int(draft_pos)

      # create key if it does not exist
      if not pos in minutes_per_draft_pos:
        minutes_per_draft_pos[pos] = []

      minutes_per_draft_pos[pos].append(int(minutes))

avg_minutes_per_draft_pos = []
for pos in minutes_per_draft_pos:
  minutes_list = minutes_per_draft_pos[pos]
  avg_min_played = mean(minutes_list)
  avg_minutes_per_draft_pos.append(avg_min_played)
  print("{0} - {1}".format(pos, avg_min_played))

# print(avg_minutes_per_draft_pos)