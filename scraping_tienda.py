# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 01:02:39 2018

@author: isma
"""
import requests 
import csv
import time
import sys
from bs4 import BeautifulSoup



def stringEliminarapartirdeuncaracter(cadena, caracter):
    num_apariciones = cadena.count(caracter) 
    if num_apariciones>0:
        pos_caracter =cadena.find(caracter) 
        return cadena[0:pos_caracter]

#funcion que recorre un sitemap que recibe cómo parámetro y devuelve la lista de urls
def listadoPaginasSiteMap(sitemap_url,tag):
    page_site_map = requests.get(sitemap_url)
    sitemap = BeautifulSoup(page_site_map.content, "lxml")
    tags = sitemap.find_all(tag)
    lista_paginas=[]
    for pagina_site in tags:
        print (pagina_site.get_text().strip())
        lista_paginas.extend([pagina_site.get_text().strip()])
    return lista_paginas


#funcion que crea un csv a partir de una lista
def crearficherocsv(nombrefichero,lista):    
   
    hoy=  time.strftime("%y%m%d")
    fichero =  str(hoy)+"_"+nombrefichero+'.csv'
    with open ( fichero , 'w' , newline = '') as csvfile:
    #with open ( fichero , 'w' , newline = '', encoding="utf-8" ) as csvfile:
       spamwriter = csv.writer(csvfile, delimiter = ';' ,
                               quotechar = '|' , quoting = csv.QUOTE_MINIMAL)
       for listaitem in lista:
           try:
               print(listaitem)
               spamwriter.writerow(listaitem)
           except ValueError:
               print("Algo ha ido mal al escribir el fichero")
       
          
       
#recupera todos los productos de una determinada pagina
def recuperaProductosPagina(url):
    #carga una página que recibe como parametro, a priori recibe páginas que contienen listados de productos
    #page = requests.get("https://www.mediamarkt.es/es/category/_c%C3%A1maras-r%C3%A9flex-701197.html")
    page = requests.get(url)
    page_soup = BeautifulSoup(page.content,"lxml")

    #listado de productos
    #todos los productos tienen las siguientes secciones
    #<div class="product-wrapper
    #    <aside class="product-photo">
    #    <aside class="product-price alt">
    #    <div class="content ">
    
    #recuperamos la categoria de los productos


    listaproductos_pagina=[] # lista en la cual guardamos la información de todos los productos

    h1_categoria =page_soup .find("h1")
    if (h1_categoria is None): 
        return listaproductos_pagina
    categoria_text= h1_categoria.get_text().strip()
    categoria_text= stringEliminarapartirdeuncaracter(categoria_text,"(")  #funcio que se queda con el substring 
    categoria_text=str(categoria_text).strip()
    

    #recuperamos todos los productos de la lista 
    for product in page_soup.find_all("div", {"class": "product-wrapper"}):
        
        item_producto=[1,2,3,4,5,6]
      
        item_producto[0]= categoria_text
        
        #producto_id
        producto_id_text = product.get("data-modelnumber")
        item_producto[1]=producto_id_text
        
        #producto_nombre
        h2_producttitle=product.find("h2")
        producto_nombre = h2_producttitle.get_text().strip()
        producto_nombre= producto_nombre.replace(";",",")
        item_producto[2]=producto_nombre 
        
        #producto manufacturer
        div_content = product.find("div", {"class": "content"})
        imgss= div_content.findChildren("img" , recursive=True)
        item_producto[3]=""
        for img in imgss:
            marca = img.get("alt")
            item_producto[3]=marca
            #print(marca)
            break;
    
        #producto_precio
        div_price = product.find("div", {"class": "price"})
        if div_price is None:
            item_producto[4]=""
        else:
            precio =div_price.get_text().strip();
            producto_precio= precio.replace(",-","")
            item_producto[4]=producto_precio
         
        #producto_precio_anterior
        producto_precio_ant="SINDESCUENTO"
        div_price_old = product.find("div", {"class": "price-old"})
        if div_price_old is None:
            producto_precio_ant="SINDESCUENTO"
        else:
            precio_tmp =div_price_old.get_text().strip()
            producto_precio_ant= precio_tmp.replace(",-","")
        item_producto[5]=producto_precio_ant
        listaproductos_pagina.append(item_producto) 
    return listaproductos_pagina
    
  




#recuperamos todas las páginas que contienen listas de productos
lista_paginas = listadoPaginasSiteMap("https://www.mediamarkt.es/sitemap/sitemap-productlist.xml", "loc")

#lista_paginas= [1]
#lista_paginas[0]="https://www.mediamarkt.es/es/category/_inal%C3%A1mbricos-702527.html"


listaproductos=[] # lista en la cual guardamos la información de todos los productos de todas las paginas

aux =1

#iteramos por todas las listas de productos
for pagina_url in lista_paginas:
    print( "pagina_url: " +str(aux)+ " " + pagina_url)
    productos_recuperados =recuperaProductosPagina(pagina_url) 
    listaproductos.extend(productos_recuperados)
    #cada lista de productos puede tener a su ver paginacion
    paginacion =2
    while productos_recuperados != []:
        nueva_url = pagina_url + "?searchParams=&sort=&view=&page=" + str(paginacion)
        paginacion = paginacion + 1
        productos_recuperados =recuperaProductosPagina(nueva_url) 
        listaproductos.extend(productos_recuperados)
        print(paginacion)
    aux = aux +1
#    if aux >4:
#        break
crearficherocsv("listaproductos",listaproductos)



