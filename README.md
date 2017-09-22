# HaliHoops - Ball is life

This aim of this repository is to create a suite of Python/R functions cabable of scraping all the NBA data stored on basketball-reference.com, performing statistical analysis on said data, and creating high-quality plots and/or applications to present the results of the analysis.

Scraping

As of the last update, per_game_seasons_srape.py module has the following functions:

get_all_players()
Returns a dataframe whose two columns are the names of all NBA/ABA players in history, and the corresponding webpage URLS.

per_game_frame(url)
Takes an NBA player's URL as input and returns a dataframe of their standard Per Game statistics for every season of their career, as well as their career averages. This function works on over 99% of all player pages on BBR.
