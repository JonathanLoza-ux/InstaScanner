import json

def cazar_datos_meta(datos, extraidos=None):
    if extraidos is None:
        extraidos = {}

    if isinstance(datos, dict):
        if 'string_list_data' in datos and isinstance(datos['string_list_data'], list) and len(datos['string_list_data']) > 0:
            item = datos['string_list_data'][0]
            ts = item.get('timestamp', 0)
            
            if 'value' in item and item['value']:
                extraidos[item['value']] = ts
            elif 'title' in datos and datos['title']:
                extraidos[datos['title']] = ts

        for valor in datos.values():
            cazar_datos_meta(valor, extraidos)

    elif isinstance(datos, list):
        for item in datos:
            cazar_datos_meta(item, extraidos)

    return extraidos