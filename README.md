# Greek Letter Recognition
Integrantes:

- Jared Orihuela
- Mitchel Soto
- Yoel Mantari
- Ebert Limache


# Reconocimiento de Letras Manuscritas con Flask y TensorFlow

Este proyecto es una aplicación web que permite dibujar letras manuscritas y obtener su predicción en tiempo real. Usa Flask para el backend, HTML5 para el frontend, y un modelo entrenado con TensorFlow/Keras.


## Requisito crítico: Usa solo Python 3.11

Este proyecto **no funcionará correctamente con Python 3.12 o 3.13** debido a incompatibilidades con TensorFlow.

Verifica tu versión:

```bash
python --version
```

## Instalación paso a paso

### 1. Clona el repositorio

```bash
git https://github.com/Dirac2022/greek-letter-recognition
```

---

### 2. Crea y activa el entorno virtual

#### En **Windows** (PowerShell o CMD):

```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

#### En **Linux/macOS**:

```bash
python3.11 -m venv venv
source venv/bin/activate
```


### 3. Instala las dependencias

```bash
python -m pip install --upgrade pip 
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
python app.py
```

Abre tu navegador en:

```
http://127.0.0.1:5000/

```



## Modelo

El modelo entrenado debe estar en:

```
models/modelo_letras3.h5
```

El modelo predice letras entre:

```
['A', ..., 'Z', 'a', ..., 'z', 'N', 'n', 'Ñ', 'ñ']
```

---

## Interfaz

* Permite dibujar letras manuscritas.
* Envía la imagen al backend.
* Muestra en pantalla la letra predicha.

---

## Estructura esperada

```
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── js/
│   │   └── script.js
│   └── css/
│       └── style.css
└── models/
    └── modelo_letras3.h5
```


