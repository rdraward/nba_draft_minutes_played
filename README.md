# Career Minutes Played per Draft Position

With teams amassing huge numbers of picks, I just wanted to look into possible value without taking stats other than average number of minutes played into account. I have added a *get_draft_class* API to the [basketball_reference_scraper](https://github.com/vishaalagartha/basketball_reference_scraper) and use this to get career minutes played over sets of different years.

Right now, I just gather basic minutes played per position and do an average for each draft position.

## Future work

- visualize the results
- breakout playoff minutes vs regular season minutes
- examine minutes on a playoff team vs minutes on a non-playoff team
  - similarly, minutes on an over .500 team vs minutes on a below .500 team
