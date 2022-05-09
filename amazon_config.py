from msilib.schema import Directory
from selenium import webdriver

DIRECTORY = 'reports'
NAME = 'Crema hidratante'
CURRENCY = '€'
MIN_PRICE = '10'
MAX_PRICE = '20'
FILTERS = {
    'minp' : MIN_PRICE,
    'maxp' : MAX_PRICE
}

BASE_URL = 'https://www.amazon.es/'

def get_chrome_web_driver(options):
    return webdriver.Chrome('./chromedriver.exe', chrome_options=options)

def get_web_driver_options():
    return webdriver.ChromeOptions()

def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')

def set_browser_as_incognito(options):
    options.add_argument('--incognito')