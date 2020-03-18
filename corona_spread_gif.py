from typing import Dict

import folium
import pandas as pd
import geonamescache # for countries population
geo_countries = geonamescache.GeonamesCache().get_countries_by_names()


def generate_corona_map(datasets: Dict[str: pd.DataFrame], date: str, colours: Dict[str: str]):
    """

    :param datasets:
    :param date:
    :param colours:
    :return:
    """
    # Make an empty map optimized for Europe
    m = folium.Map(location=[47, 12], zoom_start=5)
    # iterate over the datasets
    for name, dataset in datasets.items():
        if name not in colours:
            raise ValueError(f'Colour for {name} is not provided.')
        # add markers one by one on the map
        for i in range(0, len(dataset)):
            data = dataset.iloc[i]


def _add_marker(m, data: pd.Series, date: str, colour: str, norm_to_population=False):
    value = data[date]
    country = data['Country/Region']
    # multiplication factor for visualization
    visual_factor = 20
    # skip countries with 0 affected and Cruise Ship
    if value != 0 and country != 'Cruise Ship':
        # apply normalisation
        if norm_to_population:
            value /= country_population(country)
            visual_factor = 100
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
    return int(geo_countries[country]['population'])


def load_datasets(data_path: str, confirmed: bool, deaths: bool) -> Dict[str: pd.DataFrame]:
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


if __name__ == '__main__':
    create_corona_spread_gif()