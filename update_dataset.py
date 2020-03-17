# kaggle can be imported only if .kaggle/kaggle.json exists
try:
    import kaggle
except OSError as e:
    print(f'Can not import kaggle: {e}')
    print('To generate the kaggle.json follow steps at: https://adityashrm21.github.io/Setting-Up-Kaggle/')
    raise e
import pandas as pd


def download_dataset(destination_folder: str) -> str:
    """Download covid-19 dataset from kaggle.

    :param destination_folder: relative or absolute path to the destination folder.
    :return name of the dataset
    """
    user_name = 'sudalairajkumar'
    dataset_name = 'novel-corona-virus-2019-dataset'
    kaggle.api.dataset_download_files(f'{user_name}/{dataset_name}', path=destination_folder, unzip=True)
    # notify the user
    print(f'Dataset: {dataset_name} is uploaded into {destination_folder}')
    return dataset_name


def check_last_updated_date_main_ds(file_path: str) -> str:
    """Check the last recorded date in the covid_19_data.csv dataset.

    :param file_path: relative or absolute path to the dataset
    :return string of latest available date in the dataset
    """
    ds = pd.read_csv(file_path)
    latest_date = ds['ObservationDate'].max()
    return latest_date


def check_last_updated_date_ts_ds(file_path: str) -> str:
    """Check the last recorded date in the time_series_covid_19_confirmed.csv dataset.

    :param file_path: relative or absolute path to the dataset
    :return string of latest available date in the dataset
    """
    ds = pd.read_csv(file_path)
    latest_date = ds.columns[-1]
    return latest_date


def check_last_updated_date(destination_folder: str) -> None:
    """Check the last recorded date in the covid-19 datasets.

    :param destination_folder: relative or absolute path to the destination folder.
    :return:
    """
    # check main file: covid_19_data.csv
    main_ds_name = 'covid_19_data.csv'
    latest_main_ds_date = check_last_updated_date_main_ds(file_path=f'{destination_folder}/{main_ds_name}')
    # check timeseries
    ts_ds_name = 'time_series_covid_19_confirmed.csv'
    latest_ts_ds_date = check_last_updated_date_ts_ds(file_path=f'{destination_folder}/{ts_ds_name}')
    # notify user
    print(
        f'Last update of the main dataset({main_ds_name}): {latest_main_ds_date}'
        f'.\nLast update of the timeseries datasets({ts_ds_name}): {latest_ts_ds_date}')


if __name__ == '__main__':
    # authenticate the kaggle acount
    kaggle.api.authenticate()
    # download the covid-19 dataset
    destination_folder = './novel-corona-virus-2019-dataset'
    dataset_name = download_dataset(destination_folder)
    # check the latest available date of the updated dataset
    check_last_updated_date(destination_folder)