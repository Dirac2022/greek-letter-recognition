document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    const clearBtn = document.getElementById('clearBtn');
    const sendBtn = document.getElementById('sendBtn');
    const resultSpan = document.getElementById('result');
    const loadingIndicator = document.getElementById('loadingIndicator');

    let drawing = false;
    let lastX = 0;
    let lastY = 0;

    // Configuración inicial del canvas
    ctx.fillStyle = "white"; // Fondo blanco
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000000'; // Color del trazo (negro)
    ctx.lineWidth = 12;         // Grosor del trazo (ajústalo según tu modelo)
    ctx.lineCap = 'round';      // Terminaciones de línea redondeadas
    ctx.lineJoin = 'round';     // Uniones de líneas redondeadas

    function getPos(canvasDom, event) {
        const rect = canvasDom.getBoundingClientRect();
        let clientX, clientY;
        if (event.touches) { // Evento táctil
            clientX = event.touches[0].clientX;
            clientY = event.touches[0].clientY;
        } else { // Evento de mouse
            clientX = event.clientX;
            clientY = event.clientY;
        }
        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    }

    function startDrawing(e) {
        drawing = true;
        const pos = getPos(canvas, e);
        [lastX, lastY] = [pos.x, pos.y];
        if (e.touches) e.preventDefault(); // Prevenir scroll en táctiles
    }

    function draw(e) {
        if (!drawing) return;
        if (e.touches) e.preventDefault(); // Prevenir scroll en táctiles

        const pos = getPos(canvas, e);
        const currentX = pos.x;
        const currentY = pos.y;

        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(currentX, currentY);
        ctx.stroke();

        [lastX, lastY] = [currentX, currentY];
    }

    function stopDrawing() {
        if (!drawing) return;
        drawing = false;
        ctx.beginPath(); // Resetea el path actual para el siguiente trazo
    }

    // Eventos del mouse
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing); // Detener si el mouse sale

    // Eventos táctiles
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
    canvas.addEventListener('touchcancel', stopDrawing);


    clearBtn.addEventListener('click', () => {
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath(); // Asegurar que se resetea el path
        resultSpan.textContent = '-';
        enableControls(); // Habilitar controles si estaban deshabilitados
    });

    sendBtn.addEventListener('click', async () => {
        disableControls(); // Bloquear canvas y botones
        resultSpan.textContent = '-';

        // Obtener la imagen del canvas como data URL (PNG)
        const imageDataUrl = canvas.toDataURL('image/png');

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageDataUrl }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error del servidor: ${response.status}`);
            }

            const data = await response.json();
            resultSpan.textContent = data.prediction;

        } catch (error) {
            console.error('Error al enviar el dibujo:', error);
            resultSpan.textContent = `Error: ${error.message}`;
        } finally {
            enableControls(); // Desbloquear canvas y botones
        }
    });

    function disableControls() {
        canvas.style.pointerEvents = 'none'; // Bloquea interacciones con el canvas
        canvas.style.opacity = '0.7';
        sendBtn.disabled = true;
        clearBtn.disabled = true;
        loadingIndicator.style.display = 'block';
    }

    function enableControls() {
        canvas.style.pointerEvents = 'auto';
        canvas.style.opacity = '1';
        sendBtn.disabled = false;
        clearBtn.disabled = false;
        loadingIndicator.style.display = 'none';
    }
});
