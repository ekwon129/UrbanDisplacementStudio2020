import pandas

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
