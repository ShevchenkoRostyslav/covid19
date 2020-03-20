from typing import Dict

import folium
import pandas as pd
import geonamescache # for countries population
geo_countries = geonamescache.GeonamesCache().get_countries_by_names()


def generate_corona_map(datasets: Dict[str, pd.DataFrame], date: str, colours: Dict[str, str]):
    """Generate a single folium map from datasets for a given date.

    :param datasets: timeseries datasets for confirmed and/or deaths
    :param date: date string with a foramt mm/dd/yy
    :param colours: dataset-name / colour to visualize
    :return: folium map
    """
    # Make an empty map optimized for Europe
    m = folium.Map(location=[47, 12], zoom_start=5)
    # iterate over the datasets
    for name, dataset in datasets.items():
        if name not in colours:
            raise ValueError(f'Colour for {name} is not provided.')
        # iterate through the countries
        for i in range(0, len(dataset)):
            data = dataset.iloc[i]
            # add marker to the map
            _add_marker(m, data, date=date, colour=colours[name], norm_to_population=False)
    return m

def _add_marker(m, data: pd.Series, date: str, colour: str, norm_to_population=False):
    value = data[date]
    country = data['Country/Region']
    # multiplication factor for visualization
    visual_factor = 10
    # skip countries with 0 affected and Cruise Ship
    if value > 0 and country not in ['Cruise Ship', 'San Marino', 'Holy See']:
        # apply normalisation
        if norm_to_population:
            value /= country_population(country)
            visual_factor = 1.5e8
        marker = folium.Circle(
              location=(data['Lat'], data['Long']),
              popup=country+' '+value.astype(str),
              radius=float(value*visual_factor),
              color=colour,
              fill=True,
              fill_color=colour
           )
        # add marker to the map
        marker.add_to(m)


def country_population(country_name: str) -> int :
    """Lookup the country population from external resources.

    :param country_name: name of the country
    :return: population of the country
    """
    country = country_name
    if country == 'US': country = 'United States'
    if country == 'Holy See': country = 'Vatican'
    if country == 'Korea, South': country = 'South Korea'
    if country == 'Taiwan*': country = 'Taiwan'
    if country == 'Congo (Kinshasa)': country = 'Democratic Republic of the Congo'
    if country == "Cote d'Ivoire": country = 'Ivory Coast'
    if country == 'occupied Palestinian territory': country = 'Palestinian Territory'
    if country == 'Congo (Brazzaville)': country = 'Republic of the Congo'
    if country == 'The Bahamas': country = 'Bahamas'
    if country == 'The Gambia': country = 'Gambia'
    return int(geo_countries[country]['population'])


def load_datasets(data_path: str, confirmed: bool, deaths: bool) -> Dict[str, pd.DataFrame]:
    """Load timeseries datasets for confirmed and/or deaths.

    :param data_path: path to the novel-corona-virus-2019-dataset
    :param confirmed: whether load confirmed cases data
    :param deaths: whether load deaths data
    :return dict with name:pd.DataFrame entries
    """
    # sanity check
    if not confirmed and not deaths:
        raise ValueError('Neither confirmed nor deaths have been selected. At least one of the datasets have to be picked')
    # load the datasets
    keys = []
    if confirmed: keys.append('confirmed')
    if deaths: keys.append('deaths')
    dataset = {name: pd.read_csv(f'{data_path}/time_series_covid_19_{name}.csv') for name in keys}
    return dataset


def create_corona_spread_gif():
    date='3/17/20'
    datasets = load_datasets('novel-corona-virus-2019-dataset', confirmed=True, deaths=True)
    colours = {'deaths': 'black', 'confirmed': 'crimson'}
    corona_map = generate_corona_map(datasets, date, colours=colours)
    corona_map.save('mymap.html')





if __name__ == '__main__':
    create_corona_spread_gif()