from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def get_all_players():

    """
    By iterating over all 25 pages of NBA players (there are no last names beginning with X), and pulling their names and URLS with
    the internal function letter_player_frame, this function generates a dataframe consisting of every NBA/ABA player
    in history, and the URLS corresponding to their BBR pages.
    """

    ###INTERNAL FUNCTIONS ##########################################################################################

    def letter_player_frame(url):
        """
        This function takes as input a URL corresponding to a page listing all NBA players in history
        whose last name begin with a particular letter, and returns a data frame consisting of
        the names of every player on the page, and the URL corresponding to their BBR page
        """
        player_base_string = 'https://www.basketball-reference.com'

        html = urlopen(url)                 #Get html data
        soup = BeautifulSoup(html, 'lxml')  #Convert to Soup object

        a_list = soup.findAll('tbody')[0].findAll('a')#Find all <a tags

        link_list = [i.get("href") for i in a_list] # Get the links
        name_list = [i.contents[0] for i in a_list] # Get the text associated with the link

        player_names = [name_list[k] for k in range(len(link_list)) if link_list[k][:4] == '/pla'] #Keep only tags corresponding to players
        player_urls =  [link_list[k] for k in range(len(link_list)) if link_list[k][:4] == '/pla']

        player_urls = [(player_base_string + k) for k in player_urls] #Append base string to player urls

        url_array = np.array(player_urls)
        name_array = np.array(player_names)

        df=pd.DataFrame({'Name':name_array, 'URL':url_array})

        for k in range(df.shape[0]):
            df.iloc[k].Name = df.iloc[k].Name.replace(" ", "-") #Replace spaces with hyphens

        return df

    ############################################################################################################################################

    letter_base_string = 'https://www.basketball-reference.com/players/'

    letters = ['a/', 'b/', 'c/', 'd/', 'e/', 'f/', 'g/', 'h/', 'i/', 'j/', 'k/', 'l/', 'm/', 'n/', 'o/', 'p/', 'q/', 'r/', 's/', 't/', 'u/', 'v/', 'w/', 'y/', 'z/']
    letter_page_list = [(letter_base_string + k) for k in letters]

    frames = []

    for k in letter_page_list:
        frames.append(letter_player_frame(k)) #Add to list of frames

    return pd.concat(frames, ignore_index = True) #Concatenate all 25 dataframes together



def per_game_frame(url):
    """
    Takes a player's BBR page URL as input, and returns a cleaned dataframe containing
    their Per Game statistics for every full season they've played, as well as their career totals.
    """

    #INTERNAL FUNCTIONS ################################################################################

    def df_trim(df):
        """
        This function takes a data frame as input, locates the empty row (if there is one)
        and drops it along with all rows beneath it. If there is no empty row, the output is just
        the dataframe that was input.
        """
        output = df                                  # Default case involves no trimming

        for k in range(df.shape[0]):

            if df.Tm[k] == '':                        #The Time column is first empty in the career totals row

                good_indices = [i for i in range(k+1)]       #Every index less than or equal to that of the career totals row
                output = df.loc[np.array(good_indices), :]  #Drop the unwanted rows
                break

        return output

    def drop_repeats(df):
        """
        This function takes a dataframe as input, and drops every row that does not
        correspond to a full NBA season. It does so by dropping every row whose Age element is equal
        to that of the row above it. (First row of a given age is always the total for the year)
        """
        repeats = []  #List to hold indices of rows corresponding to partial seasons

        for k in range(1, df.shape[0]):

            if df.Season[k] == df.Season[k-1]:
                repeats.append(k)

        return df.drop(df.index[repeats])

    def drop_years_off(row_list):
        """
        This function takes the list of rows of data scraped from a players Per Game Table,
        and drops all rows corresponding to years where the players did not player in the league, e.g
        temporary retirements, injuries, etc.
        """
        bad_indices = []

        for k in range(len(row_list)-1, -1, -1): #Looping backwards over the list
            if len(row_list[k]) < len(row_list[0]):  #If the row doesn't have enough elements, drop it
                bad_indices.append(k)

        for k in bad_indices:
            row_list.pop(k)

        return row_list
    ##################################################################################################################

    html = urlopen(url)                 #Get html data
    soup = BeautifulSoup(html, 'lxml')  #Convert to Soup object

    column_headers = [th.getText() for th in soup.findAll('tr')[0].findAll('th')] #Get column headers

    data_rows = soup.findAll('tr')[1:]  #Don't include first row of data (We already have the column headers)
    data = [[td.getText() for td in data_rows[i].findAll('td')] for i in range(len(data_rows))] #Extract text data from table

    good_data = drop_years_off(data)  #Drop any years where the player did not play

    df_raw = pd.DataFrame(good_data, columns = column_headers[1:]) #Season data must be scraped seperately, so omit the first column

    df_raw_trim = df_trim(df_raw)      #Drop any extra rows (if a player ever changed teams)

    #Insertion of Season column
    a_list = soup.findAll('tbody')[0].findAll('th')  #Find all <th tags
    a_list = [k.text for k in a_list]                #Extract all text from tags
    season_list = [k for k in a_list if len(k) == 7 ]  #Any element that is not 7 characters long is not a Season entry
    season_array = np.array(season_list)             #Convert to an array
    season_array = np.append(season_array, 'Career') #Append 'Career' to end of column

    df_raw_trim['Season'] = season_array             #Insert Season column into dataframe

    df = drop_repeats(df_raw_trim)                   #Drop any partial seasons (mid-season trades)

    return df                                       #Output cleaned dataframe
