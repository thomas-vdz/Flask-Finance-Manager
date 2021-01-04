# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 15:05:15 2021

@author: thoma
"""

from webApp import create_app, db
import pandas as pd
import requests
import time
import json
from progress.bar import IncrementalBar
from webApp.models import Product

app = create_app()
app.app_context().push()
db.init_app(app)
db.drop_all()
db.create_all()

products = pd.read_csv("H:\\OneDrive\\De Streng BV\\Backup producten\\updated_products-3-1.csv")
main_prod = products.loc[pd.isnull(products["Title"]) == False]



products = main_prod['Handle']
def get_product_id(handle):
    url_prod = "https://46f8dd5faf7e0fb9770b2b12e06701b4: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@fourniturenweb.myshopify.com/admin/api/2020-10/products.json?handle="+handle
    api_products = requests.get(url_prod).content
    product = json.loads(api_products)['products']
    if not product:
        return None
    else:
        time.sleep(0.5)
        return product[0]['id']
    
    
bar = IncrementalBar('Uploading images', max = 2356)  
for prod in products:
    product_id = get_product_id(prod)
    p = Product(product_id=product_id, handle=prod)
    db.session.add(p)
    db.session.commit()
    bar.next()

bar.finish()



'''
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 13:42:34 2021

@author: thoma
"""

from webApp import create_app, db
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import json
from progress.bar import IncrementalBar
from webApp.models import Product

app = create_app()
app.app_context().push()
db.init_app(app)
db.drop_all()
db.create_all()

products = pd.read_csv("H:\\OneDrive\\De Streng BV\\Backup producten\\updated_prod-30-11.csv")
main_prod = products.loc[pd.isnull(products["Title"]) == False]

products = main_prod['Handle']
def get_product_id(handle):
    url_prod = "https://46f8dd5faf7e0fb9770b2b12e06701b4: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@fourniturenweb.myshopify.com/admin/api/2020-10/products.json?handle="+handle
    api_products = requests.get(url_prod).content
    product = json.loads(api_products)['products']
    if not product:
        return None
    else:
        time.sleep(0.5)
        return product[0]['id']
    
    
bar = IncrementalBar('Uploading images', max = 2356)  
for prod in products:
    product_id = get_product_id(prod)
    p = Product(product_id=product_id, handle=prod)
    bar.next()

bar.finish()




product = {}
product['handle'] = 'art-bw251-band'
product['product_id'] = str(get_product_id(product['handle']))

url_single_product = 'https://46f8dd5faf7e0fb9770b2b12e06701b4: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@fourniturenweb.myshopify.com/admin/api/2021-01/products/6107671298231/metafields.json'

url = "https://46f8dd5faf7e0fb9770b2b12e06701b4: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@fourniturenweb.myshopify.com/admin/api/2021-01/locations.json"



r = requests.get(url_single_product).content
data = json.loads(r)

product_dict = data['product']

variants = []

for variant in product_dict['variants']:
    variants.append({'id':variant['id'], 'inventory_policy':"continue",'inventory_quantity':2000 })

headers = {"Accept": "application/json", "Content-Type": "application/json"}
API_endpoint= 'https://46f8dd5faf7e0fb9770b2b12e06701b4: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@fourniturenweb.myshopify.com/admin/api/2021-01/products/'+ product['product_id']  +'metafields.json'

payload = {
    "product": {
        "id": 6107671298231,
        "variants": variants
        },
        "metafields": [
      {
        "key": "new",
        "value": "newvalue",
        "value_type": "string",
        "namespace": "global"
      }
    ]

    
 }


response = requests.put(url_single_product, headers=headers,  json=payload)

metafields = data['metafields']
shortDescription = [dic['value'] for dic in metafields if dic['key'] == 'shortDescription']
levertijd = [dic['value'] for dic in metafields if dic['key'] == 'levertijd']
fabriek = [dic['value'] for dic in metafields if dic['key'] == 'fabriek']
minimum_info = [dic['value'] for dic in metafields if dic['key'] == 'aantal-tonen']





'''