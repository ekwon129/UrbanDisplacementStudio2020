import pandas as pd
from shapely.geometry import Point, Polygon, shape
import geopandas as gpd
import pyproj
from shapely.ops import transform
from functools import partial


def geometrize_tweets(df):
    """
    Convert DataFrame of tweets into GeoDataFrames based on lat/lon coords.
    
    Parameters
    ----------
    data : pd.DataFrame
        Must contain columns 'lat' and 'lon' containing lat/lon coordinates
        
    Returns
    -------
    gpd.geodataframe.GeoDataFrame
    
    """
    # Create a shapely.geometry.Point for each tweet
    geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
    crs = {'init':'epsg:4326'}
    
    # Convert to GeoDataFrame, where each tweet's geometry is assigned to the lat/lon coords
    return gpd.GeoDataFrame(df, crs=crs, geometry=geometry)


def convert_shapefile_crs(shapefile):
    """
    Convert shapefile CRS to WGS84 (epsg:4326).
    Function may take a while to run.
    Source: https://gis.stackexchange.com/a/127432
    
    Parameters
    ----------
    shapefile : geopandas.GeoDataFrame
    
    Returns
    -------
    shapefile : geopandas.GeoDataFrame
        Contains updated 'geometry' column
    """
    in_proj = pyproj.Proj(shapefile.crs)
    out_proj = pyproj.Proj(init='epsg:4326')
    
    project = partial(
        pyproj.transform,
        in_proj,
        out_proj
    )
    shapefile['geometry'] = [transform(project, geom) for geom in shapefile['geometry']]
    
    return shapefile


def find_frequencies(series, pat, case=False, ratio=False):
    """
    Find the number (or ratio) of times that a pattern occurs in a list of tweets.
    
    Parameters
    ----------
    series : pd.Series
        Column of text containing tweets. Must be dtype 
    
    pat : string
        Regular expression to check against `series`. 
        
    case : boolean (optional, default=False)
        If True, comparisons are case-sensitive (e.g. 'pattern' != 'PaTtErN')
        If False, comparisons are case-insensitive. (e.g. 'pattern' == 'PaTtErN')
        
    ratio : boolean (optional, default=False)
        If True, return the ratio (number_of_matches) / (number_of_tweets).
        If False, return a tuple (number_of_matches, number_of_tweets).
        
    Returns
    -------
    integer or float
    
    """
    n = len(series)
    num_matches = series.str.contains(pat, case=case).sum()
    
    if ratio:
        return num_matches / n
    else:
        return num_matches, n