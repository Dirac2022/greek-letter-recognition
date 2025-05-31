from flask import Flask, render_template, request, jsonify, redirect, url_for
import base64
import io
from PIL import Image
import numpy as np
import re
import tensorflow as tf
import os
import datetime
from google.cloud import storage
import json # <<--- AÑADIDO para parsear el JSON

GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'images_dump') # 👈 IMPORTANT: CHANGE THIS or set in Railway

# Inicialización del cliente de GCS
storage_client = None
bucket = None

# Intenta cargar las credenciales desde la variable de entorno de Railway
gcp_creds_json_str = os.getenv('GCP_CREDENTIALS_JSON')

if gcp_creds_json_str:
    try:
        gcp_creds_dict = json.loads(gcp_creds_json_str)
        storage_client = storage.Client.from_service_account_info(gcp_creds_dict)
        if GCS_BUCKET_NAME:
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            print(f"✅ Conectado al bucket de GCS: {GCS_BUCKET_NAME} usando credenciales de env var.")
        else:
            print("✅ Cliente GCS inicializado desde env var, pero GCS_BUCKET_NAME no está configurado.")
            storage_client = None # No podemos operar sin un nombre de bucket
    except json.JSONDecodeError as e:
        print(f"⚠️ ADVERTENCIA: Error al decodificar GCP_CREDENTIALS_JSON. Error: {e}")
    except Exception as e:
        print(f"⚠️ ADVERTENCIA: No se pudo inicializar el cliente de GCS desde env var. Error: {e}")
else:
    print("⚠️ ADVERTENCIA: La variable de entorno GCP_CREDENTIALS_JSON no está configurada.")
    print("   Para desarrollo local sin esta variable, asegúrate de que GOOGLE_APPLICATION_CREDENTIALS (ruta a archivo) esté seteada.")
    try:
        storage_client = storage.Client() # Intentará usar GOOGLE_APPLICATION_CREDENTIALS si está seteado
        if GCS_BUCKET_NAME:
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            print(f"✅ Conectado al bucket de GCS: {GCS_BUCKET_NAME} usando GOOGLE_APPLICATION_CREDENTIALS (local).")
        else:
             print("✅ Cliente GCS inicializado desde GOOGLE_APPLICATION_CREDENTIALS (local), pero GCS_BUCKET_NAME no está configurado.")
             storage_client = None
    except Exception as e:
        print(f"⚠️ ADVERTENCIA: No se pudo inicializar el cliente de GCS usando GOOGLE_APPLICATION_CREDENTIALS (local). Error: {e}")

# Lista de letras según los índices que predice el modelo
classes = ['alpha', 'beta', 'epsilon', 'gamma', 'kappa', 'nu', 'rho', 'theta', 'upsilon']

# Carga del modelo .h5
try:
    model = tf.keras.models.load_model('models/best_letter_classifier.h5')
    print("✅ Modelo cargado exitosamente.")
except Exception as e:
    print(f"⚠️ ADVERTENCIA: No se pudo cargar el modelo. Error: {e}")
    model = None

app = Flask(__name__)

def preprocess_image_for_model(image_data_url, target_size=(28, 28)):
    """
    Preprocesa la imagen de DataURL para que coincida con la entrada del modelo.
    Convierte a RGBA, fondo blanco, escala de grises, resize, normaliza y añade batch + canal.
    """
    try:
        # Decodifica la imagen base64
        image_data = re.sub(r'^data:image/.+;base64,', '', image_data_url)
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))

        # Asegura canal alfa
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Fondo blanco
        background = Image.new('RGBA', img.size, (255, 255, 255))
        img_on_white = Image.alpha_composite(background, img)
        img_gray = img_on_white.convert('L') # Convertir a escala de grises

        # Redimensiona al tamaño esperado
        img_resized = img_gray.resize(target_size, Image.Resampling.LANCZOS)

        # Normaliza a [0,1]
        arr = np.array(img_resized) / 255.0

        # Añade dimensiones: (1, H, W, 1)
        arr = np.expand_dims(arr, axis=0)
        arr = np.expand_dims(arr, axis=-1)

        return arr

    except Exception as e:
        print(f"Error preprocesando la imagen para el modelo: {e}")
        return None

@app.route('/')
def index():
    return redirect(url_for('entrenamiento'))

@app.route('/entrenamiento')
def entrenamiento():
    return render_template('entrenamiento.html')

@app.route('/prediccion')
def prediccion():
    return render_template('prediccion.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        image_data_url = data.get('image')
        # Asegúrate que el preprocesamiento no dependa de GCS
        processed = preprocess_image_for_model(image_data_url)


        if processed is None:
            return jsonify({'error': 'Error al procesar la imagen'}), 400

        if model is not None:
            preds = model.predict(processed)
            pred_idx = int(np.argmax(preds[0]))
            predicted = classes[pred_idx]
            print(f"✅ Predicción del modelo: {predicted}")
        else:
            predicted = "(simulado - modelo no cargado)"
            print(f"🛈 Predicción simulada: {predicted}")

        return jsonify({'prediction': predicted})

    except Exception as e:
        print(f"Error en el endpoint /predict: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_training_image', methods=['POST'])
def save_training_image():
    # Verifica si el cliente y el bucket están disponibles
    if not storage_client or not bucket:
        print("Error: GCS no configurado. Storage_client o bucket es None.")
        return jsonify({'error': 'Google Cloud Storage no está configurado o no disponible en el servidor.'}), 503

    try:
        data = request.get_json()
        image_data_url = data.get('image_data_url')
        letter_name = data.get('letter')

        if not image_data_url or not letter_name:
            return jsonify({'error': 'Faltan datos de imagen o nombre de letra.'}), 400

        try:
            header, encoded = image_data_url.split(',', 1)
            image_bytes = base64.b64decode(encoded)
        except ValueError:
            return jsonify({'error': 'Formato de Data URL inválido.'}), 400
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        gcs_filename = f"training_data/{letter_name}/{letter_name}_{timestamp}.png"

        blob = bucket.blob(gcs_filename) # bucket ya está definido globalmente si la conexión fue exitosa
        blob.upload_from_string(image_bytes, content_type='image/png')

        print(f"✅ Imagen guardada en GCS: gs://{GCS_BUCKET_NAME}/{gcs_filename}")
        return jsonify({'success': True, 'message': f'Imagen guardada como {gcs_filename} en GCS.'}), 200

    except Exception as e:
        print(f"Error en /save_training_image: {e}")
        return jsonify({'error': f'Ocurrió un error interno al guardar la imagen: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port, debug=False)