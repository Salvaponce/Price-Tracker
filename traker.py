import datetime
import json
import re
import time
import amazon_config as ac
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class GenerateReport:
    def __init__(self, file_name, filters, base_link, currency, data):
        self.file_name = file_name
        self.filters = filters
        self.base_link = base_link
        self.currency = currency
        self.data = data
        report = {
            'name': self.file_name,
            'date': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'best_item': self.get_best_item(),
            'currency': self.currency,
            'filters': self.filters,
            'base_link': base_link,
            'products': self.data
        }
        print('Creando reporte')
        with open(f'{ac.DIRECTORY}/{self.file_name}.json', 'w') as f:
            json.dump(report, f)
        print('Hecho...')
    
    def get_best_item(self):
        try:
            return sorted(self.data, key = lambda k: k['price'])[0]
        except Exception as e:
            print(e)
            print('Problema ordenando los productos')
            return None

class AmazonAPI:
    def __init__(self, search_term, filters, base_url, currency):
        self.search_term = search_term
        self.base_url = base_url
        self.currency = currency
        options = ac.get_web_driver_options()
        ac.set_ignore_certificate_error(options)
        ac.set_browser_as_incognito(options)
        self.driver = ac.get_chrome_web_driver(options)
        self.price_filters = f'&rh=p_36%3A{filters["minp"]}00-{filters["maxp"]}00'

    def run(self):
        print(f'Buscando {self.search_term}...')
        links = self.get_products_links()
        time.sleep(10)
        if not links:
            print('Parar Script')
            return
        print(f'Tengo {len(links)} links...')
        print('Obteniendo informacion...')
        products = self.get_products_info(links)
        print(f'Tengo informacion sobre {len(products)} productos...')
        self.driver.quit()
        return products

    # Buscamos los links del producto que buscamos entre los precios que hemos elegido en amazon_config    
    def get_products_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element_by_id("twotabsearchtextbox")
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        time.sleep(5)
        self.driver.get(f'{self.driver.current_url}{self.price_filters}')
        time.sleep(5)
        result_list = self.driver.find_elements_by_class_name('s-underline-link-text')
        #result_list = self.driver.find_elements_by_id('search')
        links = []       
        try:
            #results = result_list[0].find_elements_by_xpath('//div[1]/div[1]/div/span/div[2]/div[9]/div/div/div/div/div[2]/div[1]/h2/a')
            links = set([link.get_attribute('href') for link in result_list])
            return links
        except Exception as e:
            print('SIN PRODUCTOS')
            print(e)
            return links

    def get_products_info(self, links):
        asins = self.get_asins(links)
        products = []
        for asin in asins[:5]:
            product = self.get_one_product_info(asin)
            print(len(products))
            if product:
                products.append(product)
        return products

    def get_one_product_info(self, asin):
        print(f'ID: {asin}. Obteniendo datos...')
        prod_short_url = self.base_url + '/dp/' + asin
        self.driver.get(f'{prod_short_url}?language=es_ES')
        time.sleep(5)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        print(title, seller, price)
        if title and seller and price:
            product_info = {
                'asin' : asin,
                'url': prod_short_url,
                'title': title,
                'seller': seller,
                'price': price
            }
            return product_info
        return None
    
    #Conseguimos el id(asin) de los poductos
    def get_asins(self, links):
        return [self.get_one_asin(p_link) for p_link in links if '/dp/' in p_link]

    def get_one_asin(self, p_link):
        return p_link[p_link.find('/dp/') + 4 : p_link.find('ref')]

    def get_title(self):
        try:
            return self.driver.find_element_by_id('productTitle').text
        except Exception as e:
            print(e)
            print(f'Titulo no encontrado')
            return None

    def get_seller(self):
        try:
            return self.driver.find_element_by_id('bylineInfo').text
        except:
            try:
                return self.driver.find_element_by_id('brand').text
            except Exception as e:
                print(e)
                print(f'Vendedor no encontrado')
                return None

    def get_price(self):
        try:
            price = self.driver.find_element_by_id('sns-base-price').text
            price = self.conver_price(price)
            return price
        except:
            try:
                price_w = self.driver.find_element_by_class_name('a-price-whole').text
                price_f = self.driver.find_element_by_class_name('a-price-fraction').text
                price = self.conver_price(price_w + ',' + price_f)
                return price
            except Exception as e:
                print(e)
                print(f'Precio no encontrado')
                return None
    
    # Convertimos el texto donde esta el precio en un numero flotante
    def conver_price(self, price):
        p_price = re.findall(r'[0-9]+', price)
        return float(p_price[0] + "." + p_price[1])    


# main class
if __name__ == '__main__':
    print('Main ok')
    amazon = AmazonAPI(ac.NAME, ac.FILTERS, ac.BASE_URL, ac.CURRENCY)
    data = amazon.run()
    GenerateReport(ac.NAME, ac.FILTERS, ac.BASE_URL, ac.CURRENCY, data)