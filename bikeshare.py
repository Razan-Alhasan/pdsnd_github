# By Eng. Razan Alhasan.

### Importing the necessary libraries
import time
import pandas as pd
import traceback
#import numpy as np => I'm not use it 

# This is the csv files dictionary.
CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

# In this method I take the user input and handle the entries to make sure they are valid.
def entry_validation(input_message, valid_inputs, invalid_message):
    
    """
    Function that verifies the user input and if there was a problem it returns a prompt
    Args:
        (str)  input_message   - the message displayed to ask the user of input
        (list) valid_inputs    - a list of enteries that are valid
        (str)  invalid_message - a message to be displayed if the input is invalid
    Returns:
        (str)  input           - returns the input when it's valid
    """
    while True:
        input_value = input(f"\n{input_message}\n").strip().lower()
        if input_value in valid_inputs:
            return input_value
        print(invalid_message)

# In this method get the filters inputted by the user.
def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city  - name of the city to analyze.
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day   - name of the day of week to filter by, or "all" to apply no day filter
    """
    print('\nHello! Let\'s explore some US bikeshare data!')

    # In those cases an invalid input is handled by asking the user to try again until it's true input
    
    """ City input """
    city_input_message = "Which City would like to explore? All, Chicago, New york city, Or Washington?"
    city_invalid_message = "Try to enter another city that is either: Chicago, New york city, Or Washington "
    city_valid_entries = ('all','new york city', 'chicago', 'washington')
    # Get user input for city (chicago, new york city, washington). 
    city = entry_validation(city_input_message, city_valid_entries,city_invalid_message)

    """ Month input """
    month_input_message = "In which of the months you want to explore? is it (all, january, february, ... , june)"
    month_invalid_message = "Try to enter the month again, it wasn't a valid month!"
    month_valid_entries = ('all','january','february','march','april','may','june','july','august','september','october','november','december')
    # get user input for month (all, january, february, ... , june)
    month = entry_validation(month_input_message, month_valid_entries, month_invalid_message)

    """ Day input """
    day_input_messgae = "What about the day you are looking for? is it (all, monday, tuesday, ... sunday)?"
    day_inavlid_message = "You entered a not valid day, try again"
    day_valid_entries = ('all','sunday','monday','tuesday','wednesday','thursday','friday','saturday')
    # get user input for day of week (all, monday, tuesday, ... sunday)
    day = entry_validation(day_input_messgae, day_valid_entries, day_inavlid_message)

    print('-'*40)
    return city, month, day

# In this method load the dataset based on which city the user inputs 
def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city  - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day   - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - Pandas DataFrame containing city data filtered by month and day
    """
    # Load data for the selected city or all cities
    if city != 'all':
        df = pd.read_csv(CITY_DATA[city])
    else:
        dfs = [pd.read_csv(path) for path in CITY_DATA.values()]
        df = pd.concat(dfs, ignore_index=True)
    
    # Convert the Start Time column to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    
    # Extract month and day of week from Start Time
    df['month'] = df['Start Time'].dt.month_name().str.lower()
    df['day_of_week'] = df['Start Time'].dt.day_name().str.lower()

    # Filter by month if applicable
    if month != 'all':
        df = df[df['month'] == month.lower()]

    # Filter by day if applicable
    if day != 'all':
        df = df[df['day_of_week'] == day.lower()]

    # Return the filtered DataFrame
    return df


## this metohd I created to clean the data 
## cleaning the data included handling missing data 
# also handle the high cardinality of dates
def clean_data(df, city):
    """
    Args:
        (pandas dataframe) df - takes a data frame with missing data probabloy and with not proper datatypes probably
        (city) df - because in the case of washington some coulmns doesn't exists
    Returns:
        (pandas dataframe) df - imputed with unknown and date handled
    """
    df = handle_dates(df, city)
    df = handle_missing(df)
    return df

# This method I created to handle missing data 
def handle_missing(df):
    """
    Handles missing data by filling or dropping  based on context.

    Args:
        df (pd.DataFrame): DataFrame with missing values.

    Returns:
        pd.DataFrame: DataFrame with missing values handled.
    """
    # Fill missing values for categorical columns
    categorical_cols = df.select_dtypes(include='object').columns
    df[categorical_cols] = df[categorical_cols].fillna('Unknown')

    # Fill missing values for numerical columns with 0
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    df[numerical_cols] = df[numerical_cols].fillna(0)

    # Alternatively, drop rows with too many missing values
    df = df[df.isnull().sum(axis=1) <= 1]


    return df

# This method I created to handle the dates
def handle_dates(df, city):
    """
    Handles date-related columns by converting to datetime and creating derived features.

    Args:
        df (pd.DataFrame): DataFrame with date columns.
        city (str): City name to determine city-specific processing.

    Returns:
        pd.DataFrame: DataFrame with date columns processed.
    """
    # Convert to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])

    # Extract components from Start Time
    df['start_month'] = df['Start Time'].dt.month_name().str.lower()
    df['start_day'] = df['Start Time'].dt.day_name().str.lower()
    df['start_year'] = df['Start Time'].dt.year
    df['start_time'] = df['Start Time'].dt.time

    # Extract components from End Time
    df['end_month'] = df['End Time'].dt.month_name().str.lower()
    df['end_day'] = df['End Time'].dt.day_name().str.lower()
    df['end_year'] = df['End Time'].dt.year
    df['end_time'] = df['End Time'].dt.time

    # Handle Birth Year for relevant cities
    if city in ('new york city', 'chicago'):
        df['Birth Year'] = pd.to_numeric(df['Birth Year'], errors='coerce')

    # Drop the original datetime columns
    df.drop(columns=['Start Time', 'End Time'], inplace=True)

    return df

# In this function I ask the user if they want to see 5 of the rows
# I use the head method build in by pandas to do that
def display_data(df):
    view_data = input('\nWould you like to view 5 rows of individual trip data? Enter yes or no\n').lower()
    start_locaction = 0
    while view_data == 'yes':
        #using iloc
        print(df.iloc[start_locaction:start_locaction+5])
        # change the start location of the head print
        start_locaction=start_locaction +5
        view_data = input("Do you want to proceed showing the next 5 rows?\n").lower()

# This method get the time travel frequent times
# to get that I used the mode built-in method
def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    # the most common month
    print('The most frequent month is: ', df['start_month'].mode()[0])
    
    # the most common day of week
    print('The most frequent day is: ', df['start_day'].mode()[0])

    # the most common start hour
    print('The most commoon start hour is: ', df['start_time'].mode()[0])

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)

# In this method I get some statics about the stations of the trip
# using mode and groupby 
def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    # most commonly used start station
    print('The most commonly used start station is: ', df['Start Station'].mode()[0] )

    # most commonly used end station
    print('The most commonly used end station is: ', df['End Station'].mode()[0] )

    # most frequent combination of start station and end station trip
    print('The most frequent combination of start station and end station trip is: ', 
          df.groupby(['Start Station','End Station']).size().idxmax())

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)

# In this method I get some statics about the trip duration 
# using sum, mean aggregation functions
def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # total travel time
    # the trip duration coulmn is in seconds 
    # to make it more readable I convert it to days by dividing it on 86400
    print('The total travel time in hours is: ', df['Trip Duration'].sum()/86400)

    # mean travel time
    print('The average travel time in minutes is: ', df['Trip Duration'].mean()/60)

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)

# In this method I get some statics about the users
def display_user_type_stats(df):
    """Displays user type statistics."""
    try:
        print("\nUser Type Statistics:")
        user_types = df['User Type'].value_counts()
        print(user_types)
    except KeyError:
        print("No 'User Type' data available in this city.")

def display_gender_stats(df):
    """Displays gender statistics if the column exists."""
    if 'Gender' in df.columns:
        print("\nGender Statistics:")
        gender_counts = df['Gender'].value_counts(dropna=True)
        print(gender_counts)
    else:
        print("\nGender data not available for this city.")

def display_birth_year_stats(df):
    """Displays birth year statistics if the column exists."""
    if 'Birth Year' in df.columns:
        print("\nBirth Year Statistics:")
        try:
            earliest_year = int(df['Birth Year'].min(skipna=True))
            most_recent_year = int(df['Birth Year'].max(skipna=True))
            most_common_year = int(df['Birth Year'].mode()[0])
            print(f"Earliest year: {earliest_year}")
            print(f"Most recent year: {most_recent_year}")
            print(f"Most common year: {most_common_year}")
        except ValueError:
            print("Unable to compute birth year statistics due to missing data.")
    else:
        print("\nBirth Year data not available for this city.")

def user_stats(df, city):
    """
    Displays statistics on bikeshare users.
    """
    display_user_type_stats(df)
    display_gender_stats(df)
    display_birth_year_stats(df)


def main():
    # start the program until the user hits no ot there exists an exception
    try:
        while True:
            # gets the filters 
            city, month, day = get_filters()

            # load the dataset
            df = load_data(city, month, day)

            # clean the dataset
            # Here I pass the city because in case the city is washington 
            # coulmns Gender and Birth Year coulmns doesn't exist 
            df= clean_data(df, city)

            # ask the user if they want to print the data
            display_data(df)

            # Display diffrent statics of the dataset
            time_stats(df)
            station_stats(df)
            trip_duration_stats(df)
            # Here I pass the city because in case the city is washington 
            # coulmns Gender and Birth Year coulmns doesn't exist 
            user_stats(df, city)

            # the user can restart and try diffrent cities if they 
            # key hit no the program will hault 
            restart = str(input('\nWould you like to restart? Enter yes or no.\n'))
            if restart.lower() != 'yes':
                break
    # Any exception that occures will be printed and traced 
    except Exception as e:
        print("The program encountered an error: ", 
            type(e).__name__, " : ", e)
        traceback.print_exc()

if __name__ == "__main__":
	main()