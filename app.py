from flask import Flask, render_template, request, jsonify, redirect, url_for
import base64
import io
from PIL import Image
import numpy as np
import re
import tensorflow as tf

# Lista de letras según los índices que predice el modelo
classes = ['A', 'E', 'K', 'R', 'U', 'a', 'e', 'k', 'r', 'u']

# Carga del modelo .h5
try:
    model = tf.keras.models.load_model('models/modelo_letras.h5')
    print("✅ Modelo cargado exitosamente.")
except Exception as e:
    print(f"⚠️ ADVERTENCIA: No se pudo cargar el modelo. Se usarán predicciones simuladas. Error: {e}")
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
        img_gray = img_on_white.convert('L')

        # Redimensiona al tamaño esperado
        img_resized = img_gray.resize(target_size, Image.Resampling.LANCZOS)

        # Normaliza a [0,1]
        arr = np.array(img_resized) / 255.0

        # Añade dimensiones: (1, H, W, 1)
        arr = np.expand_dims(arr, axis=0)
        arr = np.expand_dims(arr, axis=-1)

        return arr

    except Exception as e:
        print(f"Error preprocesando la imagen: {e}")
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
        processed = preprocess_image_for_model(image_data_url)

        if processed is None:
            return jsonify({'error': 'Error al procesar la imagen'}), 400

        if model is not None:
            # Predicción real
            preds = model.predict(processed)          # shape (1, n_clases)
            pred_idx = int(np.argmax(preds[0]))       # índice numérico
            predicted = classes[pred_idx]             # letra correspondiente
            print(f"✅ Predicción del modelo: {predicted}")
        else:
            # Simulación de respaldo
            predicted = "(simulado)"
            print(f"🛈 Predicción simulada: {predicted}")

        return jsonify({'prediction': predicted})

    except Exception as e:
        print(f"Error en el endpoint /predict: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
