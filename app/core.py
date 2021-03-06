import datetime
import json
import pathlib
import pandas as pd

def reduce_cols(df, downsample):
    """Reduce number of columns in a pandas df by skipping alternate columns

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A pandas dataframe where the first column is the title.
    downsample : int
        Factor by which to downsample dataframe. Step == input ncols // downsample

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with a reduced number of columns
    """
    title_col = df.iloc[:, 0]  # always keep title col
    last_col = df.iloc[:, -1]  # always keep data for latest day
    cols_to_reduce = df.iloc[:, 1:-1]

    ncols = cols_to_reduce.shape[1]
    step = ncols // downsample
    reduced_cols = cols_to_reduce.iloc[:, ::step]
    new_cols = pd.concat([title_col, reduced_cols, last_col], axis=1)

    return new_cols


def reduce_rows(df, downsample):
    """Reduce number of rows in a pandas df by skipping alternate rows

    Note: drops rows containing NaNs in the 'cases_mtl_0-4' column

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A pandas dataframe.
    downsample : int
        Factor by which to downsample dataframe. Step == input nrows // downsample

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with a reduced number of rows
    """
    df = df[df['cases_mtl_0-4'].notna()]  # drop rows with no age data
    last_row = df.iloc[-1, :]  # always keep data for latest day
    rows_to_reduce = df.iloc[0:-1, :]

    nrows = rows_to_reduce.shape[0]
    step = nrows // downsample
    reduced_rows = rows_to_reduce.iloc[::step, :]
    new_rows = reduced_rows.append(last_row)
    return new_rows


# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()

##### load data #####
# Montreal geojson
with open(DATA_PATH.joinpath('montreal_shapefile.geojson'), encoding='utf-8') as shapefile:
    mtl_geojson = json.load(shapefile)

# Montreal cases per borough
cases_per1000_csv = DATA_PATH.joinpath('processed', 'cases_per1000.csv')
cases_per1000_df = pd.read_csv(cases_per1000_csv, encoding='utf-8', na_values='na').dropna(axis=1, how='all')
cases_per1000_long = pd.melt(reduce_cols(cases_per1000_df, 10), id_vars='borough',
                             var_name='date', value_name='cases_per_1000')

# Montreal data
data_mtl = pd.read_csv(DATA_PATH.joinpath('data_mtl.csv'), encoding='utf-8', na_values='na')

# QC data
data_qc = pd.read_csv(DATA_PATH.joinpath('processed', 'data_qc.csv'), encoding='utf-8', na_values='na')
data_qc_recovered = pd.read_csv(DATA_PATH.joinpath('data_qc_recovered.csv'), encoding='utf-8', na_values='na')

# MTL deaths by location data
data_mtl_death_loc = pd.read_csv(DATA_PATH.joinpath('processed', 'data_mtl_death_loc.csv'),
                                encoding='utf-8', na_values='na')

# QC deaths by location data
data_qc_death_loc = pd.read_csv(DATA_PATH.joinpath('data_qc_death_loc.csv'),
                                encoding='utf-8', na_values='na')
data_qc_death_loc.columns = ['date', 'chsld', 'psr', 'home', 'other_or_unknown' ]
data_qc_death_loc['date'] = pd.to_datetime(data_qc_death_loc['date'])  # convert date str to datetime

# Last update date
# Display 1 day after the latest data as data from the previous day are posted
latest_mtl_date = datetime.date.fromisoformat(data_mtl['date'].iloc[-1]) + datetime.timedelta(days=1)
latest_update_date = latest_mtl_date.isoformat()

# Mini info boxes
latest_cases_mtl = str(int(data_mtl['cases_mtl'].dropna().iloc[-1]))
latest_deaths_mtl = str(int(data_mtl['deaths_mtl'].dropna().iloc[-1]))

latest_cases_qc = str(int(data_qc['cases_qc'].dropna().iloc[-1]))
latest_deaths_qc = str(int(data_qc['deaths_qc'].dropna().iloc[-1]))
latest_hospitalisations_qc = str(int(data_qc['hospitalisations_qc'].dropna().iloc[-1]))
latest_icu_qc = str(int(data_qc['icu_qc'].dropna().iloc[-1]))
latest_negative_tests_qc = str(int(data_qc['negative_tests_qc'].dropna().iloc[-1]))

latest_recovered_qc = str(int(data_qc_recovered['recovered_qc'].dropna().iloc[-1]))

# Make MTL histogram data tidy
mtl_age_data = reduce_rows(data_mtl, 10).melt(id_vars='date', value_vars=['cases_mtl_0-4_norm', 'cases_mtl_5-9_norm',
                                               'cases_mtl_10-19_norm', 'cases_mtl_20-29_norm',
                                               'cases_mtl_30-39_norm', 'cases_mtl_40-49_norm',
                                               'cases_mtl_50-59_norm', 'cases_mtl_60-69_norm',
                                               'cases_mtl_70-79_norm', 'cases_mtl_80+_norm',
                                          'cases_mtl_0-4_per100000_norm', 'cases_mtl_5-9_per100000_norm',
                                               'cases_mtl_10-19_per100000_norm', 'cases_mtl_20-29_per100000_norm',
                                               'cases_mtl_30-39_per100000_norm', 'cases_mtl_40-49_per100000_norm',
                                               'cases_mtl_50-59_per100000_norm', 'cases_mtl_60-69_per100000_norm',
                                               'cases_mtl_70-79_per100000_norm', 'cases_mtl_80+_per100000_norm'
                                              ],var_name='age_group', value_name='percent').dropna()
