import pandas
import geopandas as gpd
from .clean_tweets import geometrize_tweets
from .home_location import assign_home_location

def summary_stats(data):
    """
    Analyze the following:
        - Number of tweets (printed output)
        - Number of unique users (printed output)
        - Median number of tweets/user (returned output)
        - Number of tweets/user at the 99th percentile (returned output)

    Parameters
    ----------
    data : pd.DataFrame or gpd.GeoDataFrame
        DataFrame containing tweets; must contain column `u_id` for user id

    Returns
    -------
    median_tweets : int or float
        Median number of tweets/user

    pct_99_tweets : int or float
        99th percentile of tweets/user
    """
    # Number of tweets
    print("{} total tweets".format(len(data)))

    # Number of unique users
    print("{} unique users\n".format(data['u_id'].nunique()))

    # Percentiles of tweets/user (median + 99th)
    pct_50_tweets, pct_99_tweets = data.groupby('u_id').size().quantile([.50, .99])
    print("Median number of tweets/user: {} tweets".format(pct_50_tweets))
    print("99th percentile of tweets/user: {} tweets".format(pct_99_tweets))

    return pct_50_tweets, pct_99_tweets

def filter_and_home_assign(data, shapefile, lower, upper):
    """
    Find subset of data to analyze based on lower/upper bounds on tweets/user,
    then add home locations.

    Parameters
    ----------
    data : pd.DataFrame or gpd.GeoDataFrame
        DataFrame containing tweets; must contain column `u_id` for user id

    shapefile : gpd.GeoDataFrame
        Shapefile for tracts in tweets location.
        Must be in WGS84 (epsg:4326) format (to align with tweet lat/lon).

    lower, upper : int or float
        Lower (inclusive) and upper (exclusive) bounds on tweets/user.

    Returns
    -------
    filtered : gpd.GeoDataFrame
        Collection of tweets filtered by lower/upper and with tweet geographies.
        Contains new columns:
            - 'timestamp' : pd.Timestamp for time of tweet published
            - 'date' : date (int) of tweet published
            - 'hour' : 24-hour (int) of tweet published
            - 'home' : name of home location codigo (some may be NaN)
            - 'is_home' : boolean indicating whether tweet was made at home
    """
    # Filter based on lower and upper bound on tweets/user
    filtered = data.groupby('u_id').filter(lambda group: (len(group) >= lower) & (len(group) < upper))

    # Geometrize tweets (inplace) based on lat/lon
    filtered = geometrize_tweets(filtered)

    # Spatial join with tracts
    filtered = gpd.sjoin(filtered, shapefile, how='left', op='intersects')

    # Add datetime
    filtered['timestamp'] = pd.to_datetime(filtered['created_at'] // 1000, unit='s')
    filtered['date'] = filtered['timestamp'].dt.date
    filtered['hour'] = filtered['timestamp'].dt.hour

    # Add home location
    filtered['home'] = assign_home_location(filtered, SA2='SA2_MAIN16')
    filtered['is_home'] = filtered['SA2_MAIN16'] == filtered['home']

    return filtered
