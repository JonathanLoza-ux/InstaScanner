import os
import zipfile
import json
import tempfile
import shutil
from datetime import datetime
from flask import Flask, render_template, request
from nucleo import cazar_datos_meta

app = Flask(__name__)

def buscar_archivos_json(directorio):
    ruta_seguidores = None
    ruta_siguiendo = None
    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            if archivo.startswith('followers') and archivo.endswith('.json'):
                ruta_seguidores = os.path.join(raiz, archivo)
            elif archivo.startswith('following') and archivo.endswith('.json'):
                ruta_siguiendo = os.path.join(raiz, archivo)
    return ruta_seguidores, ruta_siguiendo

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'archivo_zip' not in request.files:
            return "No se subió ningún archivo", 400
        
        archivo = request.files['archivo_zip']
        if archivo.filename == '':
            return "El archivo no tiene nombre", 400
            
        if archivo and archivo.filename.endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, 'datos.zip')
            
            try:
                archivo.save(zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                ruta_seguidores, ruta_siguiendo = buscar_archivos_json(temp_dir)
                
                if not ruta_seguidores or not ruta_siguiendo:
                    shutil.rmtree(temp_dir)
                    return "❌ Error: El ZIP no contiene la información de Seguidores y Seguidos.", 400
                    
                with open(ruta_seguidores, 'r', encoding='utf-8') as f:
                    data_seguidores = json.load(f)
                with open(ruta_siguiendo, 'r', encoding='utf-8') as f:
                    data_siguiendo = json.load(f)
                    
                seguidores_info = cazar_datos_meta(data_seguidores)
                siguiendo_info = cazar_datos_meta(data_siguiendo)
                
                nombres_seguidores = set(seguidores_info.keys())
                
                lista_final = []
                for usuario, ts in siguiendo_info.items():
                    if usuario not in nombres_seguidores:
                        fecha = datetime.fromtimestamp(ts).strftime('%d/%m/%Y') if ts else "Desconocida"
                        lista_final.append({'usuario': usuario, 'fecha': fecha, 'ts': ts})
                        
                lista_final.sort(key=lambda x: x['ts'], reverse=True)
                
                resultados = {
                    'total_siguiendo': len(siguiendo_info),
                    'total_seguidores': len(nombres_seguidores),
                    'mutuos': len(nombres_seguidores.intersection(siguiendo_info.keys())),
                    'traidores': lista_final
                }
                
                shutil.rmtree(temp_dir)
                return render_template('index.html', resultados=resultados)
                
            except Exception as e:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                return f"Ocurrió un error técnico: {str(e)}", 500

    return render_template('index.html', resultados=None)

if __name__ == '__main__':
    # Render usa variables de entorno para los puertos, no necesitamos forzar nada aquí
    app.run(debug=False)