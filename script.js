const greekLetters = [
    { letter: 'alpha', weight: 1 },
    { letter: 'epsilon', weight: 1 },
    { letter: 'kappa', weight: 1 },
    { letter: 'nu', weight: 1 },
    { letter: 'rho', weight: 1 },
    { letter: 'upsilon', weight: 1 },
    { letter: 'beta', weight: 3 },    // ~20%
    { letter: 'theta', weight: 3 },   // ~20%
    { letter: 'gamma', weight: 3 }    // ~20%
];

function getRandomGreekLetter() {
    const totalWeight = greekLetters.reduce((sum, item) => sum + item.weight, 0);
    const random = Math.random() * totalWeight;
    let weightSum = 0;
    for (const item of greekLetters) {
        weightSum += item.weight;
        if (random <= weightSum) {
            return item.letter;
        }
    }
    return greekLetters[greekLetters.length - 1].letter;
}

// Prueba: generar 10,000 muestras y contar frecuencias
const testRuns = 10000;
const frequencyCounter = {};

// Inicializar contador para cada letra
greekLetters.forEach(item => {
    frequencyCounter[item.letter] = 0;
});

// Ejecutar la función muchas veces y contar resultados
for (let i = 0; i < testRuns; i++) {
    const selectedLetter = getRandomGreekLetter();
    frequencyCounter[selectedLetter]++;
}

// Calcular porcentajes y mostrar resultados
console.log("Resultados después de", testRuns, "ejecuciones:");
console.log("---------------------------------");

for (const letter in frequencyCounter) {
    const count = frequencyCounter[letter];
    const percentage = (count / testRuns * 100).toFixed(2);
    console.log(`${letter}: ${count} veces (${percentage}%)`);
}