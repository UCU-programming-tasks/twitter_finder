"""Module to create an HTML map with markers indicating Twitter friends"""
import tweepy
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from folium.plugins import MarkerCluster

YOUR_BEARER_KEY = ''
YOUR_BEARER_SECRET = ''


def init(user_agent: str = 'dyaroshevych123') -> RateLimiter:
    """
    Initialize locator and geocode.
    """
    locator = Nominatim(user_agent=user_agent)
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

    return geocode


def geocode_with_exception(loc, geocode):
    """
    Find location. If no location can be found, return None.
    """
    try:
        return geocode(loc)
    except Exception:
        return None


def add_coordinates(df: pd.DataFrame, geocode) -> pd.DataFrame:
    """
    Add coordinates information to the given DataFrame.
    """

    df['Location'] = df['Location'].apply(
        lambda loc: geocode_with_exception(loc, geocode))
    df.dropna(how='any', inplace=True)

    df['Point'] = df['Location'].apply(
        lambda loc: tuple(loc.point) if loc else None)
    df[['Latitude', 'Longitude', 'Altitude']] = pd.DataFrame(
        df['Point'].tolist(), index=df.index)

    df.drop(columns=['Point', 'Altitude'], inplace=True)
    df.dropna(how='any', inplace=True)

    return df.head(10)


def create_map(data: pd.DataFrame) -> folium.Map:
    """
    Create a map with all given locations.
    """
    mymap = folium.Map()

    marker_cluster = MarkerCluster().add_to(mymap)
    locations = list(zip(data['Latitude'].values, data['Longitude'].values))

    for idx, location in enumerate(locations):
        popup = folium.Popup(data['Username'].iloc[idx])

        folium.Marker(location, popup=popup).add_to(marker_cluster)

    folium.LayerControl().add_to(mymap)

    return mymap


def get_twitter_friends(username: str) -> pd.DataFrame:
    """
    Get a DataFrame with information about Twitter friends of a certain
    account and their locations.
    """
    # Initialize Twitter API
    auth = tweepy.OAuthHandler('bcXpN5x2fAhvz7lZ8ECSFEb12',
                               'vJiNduJRIde5pcl7qxEucZg1FbN8oRBdNwK0WFG5dIivtEDxvC')
    auth.set_access_token(YOUR_BEARER_KEY,
                          YOUR_BEARER_SECRET)
    api = tweepy.API(auth)

    # Get a list of Twitter friends of the specified account
    friends = api.friends(username)

    # Filter out friends with no specified location
    friends = list(filter(lambda friend: friend.location, friends))

    # Extract info from accounts data
    names = [friend.name for friend in friends]
    locations = [friend.location for friend in friends]

    # Build DataFrame with information about Twitter friends (username and location)
    df = pd.DataFrame(zip(names, locations), columns=['Username', 'Location'])

    return df


def main(username: str):
    """
    Main function for HTML map creation.
    """
    df = get_twitter_friends(username)

    geocode = init()
    add_coordinates(df, geocode)
    return create_map(df).get_root().render()
