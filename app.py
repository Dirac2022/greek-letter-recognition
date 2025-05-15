from flask import Flask, render_template, request, jsonify
import base64
import io
from PIL import Image 
import numpy as np
import re
import time

# (Opcional) Cargar tu modelo de Machine Learning aquí (PYTORCH O TF, cualquiera )
# import tensorflow as tf
# try:
#     model = tf.keras.models.load_model('models/tu_modelo_de_digitos.h5') # Cambia la ruta
#     print("Modelo cargado exitosamente.")
# except Exception as e:
#     print(f"ADVERTENCIA: No se pudo cargar el modelo. Se usarán predicciones simuladas. Error: {e}")
#     model = None

app = Flask(__name__)

def preprocess_image_for_model(image_data_url, target_size=(28, 28)):
    """
    Preprocesa la imagen del canvas para que coincida con la entrada del modelo.
    Esto es un EJEMPLO y DEBE SER AJUSTADO a los requerimientos de TU MODELO.
    """
    try:
        # Quita el encabezado 'data:image/png;base64,'
        image_data = re.sub('^data:image/.+;base64,', '', image_data_url)
        img_bytes = base64.b64decode(image_data)

        img = Image.open(io.BytesIO(img_bytes))

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        background = Image.new('RGBA', img.size, (255, 255, 255)) 
        img_on_white_bg = Image.alpha_composite(background, img)

        img_gray = img_on_white_bg.convert('L')

        img_resized = img_gray.resize(target_size, Image.Resampling.LANCZOS) 

        # Convertir a array numpy y normalizar (0-1 o -1-1, según tu modelo)
        img_array = np.array(img_resized)
        img_array = img_array / 255.0 # Normalizar a [0, 1]

        # 5. (IMPORTANTE) Invertir colores si es necesario:
        #    Si dibujas negro sobre blanco (canvas) y tu modelo fue entrenado con
        #    dígitos blancos sobre fondo negro (típico en MNIST), necesitas invertir.
        #    img_array = 1.0 - img_array

        # 6. Añadir dimensiones de batch y canal si el modelo lo espera
        #    (ej. (1, 28, 28, 1) para TensorFlow/Keras con formato channels_last)
        img_array = np.expand_dims(img_array, axis=0)  # Dimensión de batch
        img_array = np.expand_dims(img_array, axis=-1) # Dimensión de canal (escala de grises)

        return img_array

    except Exception as e:
        print(f"Error preprocesando la imagen: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        image_data_url = data['image'] # Esta es la imagen en formato DataURL

        # --- SIMULACIÓN DE PREDICCIÓN ---
        # Reemplaza esta sección con el preprocesamiento y la predicción de tu modelo real.
        print("Recibida imagen para predicción (simulada).")
        time.sleep(1.5) # Simular el tiempo que tomaría una predicción real

        # # --- EJEMPLO DE USO DE MODELO REAL (descomentar y adaptar si tienes uno) ---
        # processed_image = preprocess_image_for_model(image_data_url)
        # if processed_image is not None and model is not None:
        #     prediction = model.predict(processed_image)
        #     predicted_digit = str(np.argmax(prediction[0]))
        #     print(f"Predicción del modelo: {predicted_digit}")
        # elif model is None:
        #     predicted_digit = str(np.random.randint(0, 10)) + " (simulado, modelo no cargado)"
        #     print(f"Predicción: {predicted_digit}")
        # else: # Error en preprocesamiento
        #     return jsonify({'error': 'Error al procesar la imagen'}), 400
        # # --- Fin Ejemplo Modelo Real ---

        predicted_digit = str(np.random.randint(0, 10)) + " (S)" 
        print(f"Predicción simulada: {predicted_digit}")
        return jsonify({'prediction': predicted_digit})

    except Exception as e:
        print(f"Error en el endpoint /predict: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Railway usará Gunicorn, pero para desarrollo local esto funciona.
    # El puerto será asignado por Railway, pero 5000 es un default común.
    # Escuchar en 0.0.0.0 hace que sea accesible desde fuera del contenedor.
    app.run(host='0.0.0.0', port=5000, debug=True)
