from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from time import sleep
from selenium.webdriver.common.by import By
import undetected_chromedriver.v2 as uc##para nao ter problemas de login excessivo
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC

class ml_your_data:
    def __init__(self,product_name,n_pages=None):
          self.product_name=product_name#nome do produto
          self.n_pages=n_pages#numero de paginas a serem analisadas
    def ml_scrap(self):
          options=uc.ChromeOptions()
          options.add_argument('start-maximized')#iniciar maximizada para carregador os elementos
          prefs = {"profile.managed_default_content_settings.images": 2}
          options.add_experimental_option("prefs", prefs)
          driver=uc.Chrome(options=options)#criando driver com as opções desejadas
          driver.delete_all_cookies()
          driver.get('https://www.mercadolivre.com.br/')#pagina desejada
          WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @class='nav-search-input']")))#aguardar ate obter a barra de pesquisa
          search_box=driver.find_element(By.XPATH,"//input[@type='text' and @class='nav-search-input']")
          search_button=driver.find_element(By.XPATH,"//button[@type='submit' and @class='nav-search-btn']")
          search_box.click()#clicando na caixa de pesquisa para digitar
          search_box.send_keys(self.product_name)#enviando o nome do produto para a caixa de pesquisa
          sleep(1)
          search_button.click()#clicando para pesquisar
          sleep(2)
          source=driver.page_source#pegando o codigo fonte da primeira pagina
          driver.close()
          s0=BeautifulSoup(source,'html.parser')#passando para soup
          if self.n_pages is None:
              try:
                n=int(re.findall('\d+',s0.find('li',{'class':'andes-pagination__page-count'}).text)[0])#numero de urls a serem scrapados, usamos o regex para extrair numero do texto
              except:
                n=1
          else:
              n=self.n_pages
          full_data=pd.DataFrame(columns=['product_name','product_price'])##nomes e preço
          for i in range(n-1):
            if i==0:
                s0=s0.find('section',{'class':'ui-search-results ui-search-results--without-disclaimer shops__search-results'})#especificando o codigo fonte que vamos scrapar 
            product=s0.find_all('div',{'class':'ui-search-result__content-wrapper shops__result-content-wrapper'})#indo na box aonde esta o preço e nome
            product_name_one_page=[k for k in range(len(product))]
            product_price_one_page=[k for k in range(len(product))]
            for j in range(len(product)):
                product_name_one_page[j]=product[j].find('h2',{'class':'ui-search-item__title ui-search-item__group__element shops__items-group-details shops__item-title'}).string#indo para subtag aonde esta o nome
                product_price_one_page[j]=product[j].find('span',{'class':'price-tag-fraction'}).string#indo pra sub tag aonde esta o preço
                pd_data=pd.DataFrame(data={'product_name':product_name_one_page,'product_price':product_price_one_page})#armazenando as informações
            full_data=full_data.append(pd_data)
            next_url=s0.find('a',{'title':'Próxima','class':'andes-pagination__link shops__pagination-link ui-search-link'}).get('href')#pegando o link para a pagina posterior
            response=requests.get(next_url)
            data=response.content#pegando o html da page posterior
            s0=BeautifulSoup(data,'html.parser')#passando para o soup
            s0=s0.find('section',{'class':'ui-search-results ui-search-results--without-disclaimer shops__search-results'})#particionando
          return full_data