from typing import Dict
import argparse
from pathlib import Path
import datetime
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import redirect_stdout
import time
import imageio
import io

import folium
import pandas as pd
import geonamescache # for countries population
geo_countries = geonamescache.GeonamesCache().get_countries_by_names()


def generate_corona_map(datasets: dict, date: str, colours: dict, norm_to_population=False):
    """Generate a single folium map from datasets for a given date.

    :param datasets: timeseries datasets for confirmed and/or deaths
    :param date: date string with a foramt mm/dd/yy
    :param colours: dataset-name / colour to visualize
    :param norm_to_population: normalize the number of cases to the country population
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
            _add_marker(m, data, date=date, colour=colours[name], norm_to_population=norm_to_population)
    return m


def _add_marker(m, data: pd.Series, date: str, colour: str, norm_to_population: bool = False) -> None:
    """Add individual marker/circle to the folium map.

    :param m: folium map
    :param data: timeseries with cases
    :param date: str with date for which execute
    :param colour: colour of the marker
    :param norm_to_population: normalize to the population or not
    :return:
    """
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


def add_text_to_map(m, text: str, font_size: int, position: tuple = (39.7339, 24.4858)) -> None:
    """Add text to the map.

    :param m: folium map
    :param text: text to write on the map
    :param font_size: font size of the text
    :param position: Longitude and Lattitude of the text
    :return:
    """
    folium.map.Marker(
        position,
        icon=folium.features.DivIcon(
            icon_size=(150, 36),
            icon_anchor=(0, 0),
            html=f'<div style="font-size: {font_size}pt">{text}</div>',
            )
    ).add_to(m)


def country_population(country_name: str) -> int:
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
    if country == 'The Bahamas' or country == 'Bahamas, The': country = 'Bahamas'
    if country == 'The Gambia' or country == 'Gambia, The': country = 'Gambia'
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


def save_map_png(m, filename: str) -> str:
    """Hack to save folium map as png.

    :param m: folium map
    :param filename: name of the output file without extension
    :return name of the .png file
    """
    # save as html
    tmpurl='file://{path}.html'.format(path=Path(filename).absolute())
    m.save(f'{filename}.html')
    out_file = f'{filename}.png'
    screenshot_browser(tmpurl, filename=out_file)
    return out_file


def screenshot_browser(url, filename, delay=5) -> None:
    """Run Chrome browser with selenium, load the url, take a screenshot.

    :param url: url to load in Chrome
    :param filename: filename of the screenshot
    :param delay: seconds of the delay
    :return:
    """
    out = io.StringIO()
    with redirect_stdout(out):
        # run selenium
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.set_window_position(0, 0)
        browser.set_window_size(800, 800)
        browser.get(url)
        # Give the map tiles some time to load
        time.sleep(delay)
        # save the screenshot
        browser.save_screenshot(filename)
        browser.quit()


def get_list_of_dates(start_date, datasets):
    """Exract the list of dates to make a gif for.

    :param start_date: A date to start iterating from
    :param datasets: timeseries datasets for confirmed and/or deaths
    :return:
    """
    dates = [x for x in datasets.get('confirmed', 'deaths').columns[4:]]
    start_index = dates.index(start_date)
    return dates[start_index:]

def parse_cmd_args():
    """Parse cmd user input

    :return: the namespace object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default='./output')
    parser.add_argument("--input_dir", type=str, default='./novel-corona-virus-2019-dataset')
    parser.add_argument('--plot_confirmed', type=bool, default=True)
    parser.add_argument('--plot_deaths', type=bool, default=True)
    parser.add_argument('--start_date', type=str, default='2/23/20', help='mm/dd/yy')
    parser.add_argument('--normalize_to_population', type=bool, default=False, help='Normalize the number of cases to the country population')
    args = parser.parse_args()
    return args


def validate_cmd_args(args: argparse.Namespace) -> Dict:
    """Validate the cmd input

    :param args: cmd inputs
    :return:
    """
    arg_dict = vars(args)
    # validate the output dir
    try:
        Path(arg_dict['output_dir']).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise e
    # validate the input dir
    in_p = Path(arg_dict['input_dir'])
    if not in_p.exists():
        raise ValueError(f'Input directory: {arg_dict["input_dir"]} does not exist.')
    # validate whether dir contains time_series datasets
    for dtype in ['confirmed', 'deaths']:
        filename = f'time_series_covid_19_{dtype}.csv'
        if not (in_p / filename).exists() and arg_dict[f'plot_{dtype}'] == True:
            raise ValueError(f'File {filename} is not found in {arg_dict["input_dir"]}.')
    # validate start_date
    try:
        datetime.datetime.strptime(arg_dict['start_date'], '%m/%d/%y')
    except ValueError:
        raise ValueError("Incorrect data format, should be mm/dd/yy")
    return arg_dict


def create_corona_spread_gif(args: dict):
    date = args['start_date']
    # load the input data
    datasets = load_datasets(args['input_dir'], confirmed=args['plot_confirmed'], deaths=args['plot_deaths'])
    # assign colours
    colours = {'deaths': 'black', 'confirmed': 'crimson'}
    # extract available dates:
    dates = get_list_of_dates(date, datasets)
    # post_fix to the file names
    filename_postfix = ''
    if args['normalize_to_population']:
        filename_postfix += '_norm_to_population'
    screenshots = []
    # iterate through the dates
    for date in dates:
        # check if map already exist
        filename = 'map_'+date.replace('/', '_')
        filename = f'{args["output_dir"]}/{filename}{filename_postfix}'
        screenshot = filename+'.png'
        # create a screenshot if doesn't exist
        if not os.path.exists(screenshot):
            # generate a single map
            corona_map = generate_corona_map(datasets, date, colours=colours, norm_to_population=args['normalize_to_population'])
            # add author name
            add_text_to_map(corona_map, '@R.Shevchenko', font_size=13, position=(55.7, 23.4858))
            # add date to the bottom
            add_text_to_map(corona_map, date, font_size=24, position=(37.7339, 24.4858))
            # save as png
            screenshot = save_map_png(corona_map, filename=filename)
            print(f'Date {date} has been processed.')
        # append screenshot for the gif
        screenshots.append(imageio.imread(screenshot))
    # generate the gif
    gif_name = f'{args["output_dir"]}/corona{filename_postfix}'
    imageio.mimsave(f'{gif_name}.gif', screenshots)


if __name__ == '__main__':
    # read cmd arguments
    args = parse_cmd_args()
    # validate user input
    args = validate_cmd_args(args)
    # create a gif
    create_corona_spread_gif(args)