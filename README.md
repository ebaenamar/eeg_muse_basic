# Muse EEG - Guía Completa

Conecta, transmite y visualiza datos EEG de tu banda **Muse** usando Python y LSL (Lab Streaming Layer).

## 📋 Requisitos Previos

### Hardware
- **Banda Muse** (Muse 2, Muse S, o Muse original)
- **Mac** con Bluetooth (probado en macOS)
- La banda debe estar **cargada y encendida**

### Software
- **Python 3.10+** (recomendado 3.12)
- **Bluetooth activado** en tu Mac
- **Git** (para clonar el repositorio)

---

## 🚀 Instalación Paso a Paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/ebaenamar/eeg_muse_basic.git
cd eeg_muse_basic
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. (Solo macOS) Si tienes problemas con Tkinter

Si `muselsl view` da error de Tkinter, usa el visualizador alternativo incluido (`view_eeg.py`).

---

## 🎯 Uso Básico

### Paso 1: Activar Bluetooth y encender tu Muse

1. Ve a **Preferencias del Sistema → Bluetooth → Activar**
2. Enciende tu banda Muse (mantén presionado el botón hasta que parpadee)
3. Colócala en tu cabeza para mejor detección

### Paso 2: Buscar tu dispositivo Muse

```bash
source venv/bin/activate
muselsl list
```

Salida esperada:
```
Searching for Muses, this may take up to 10 seconds...
Found device Muse-XXXX, MAC Address XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

**Guarda la MAC Address**, la necesitarás para conectar.

### Paso 3: Iniciar streaming EEG

En una terminal:

```bash
source venv/bin/activate
muselsl stream --address <TU_MAC_ADDRESS>
```

Ejemplo:
```bash
muselsl stream --address 4BEE1E10-85F7-FB8C-49E2-17174042399F
```

Salida esperada:
```
Connecting to Muse: XXXXXXXX...
Connected.
Streaming EEG...
```

**Deja esta terminal abierta** mientras trabajas con los datos.

### Paso 4: Visualizar EEG en tiempo real

Abre **otra terminal**:

```bash
source venv/bin/activate
python view_eeg.py
```

Verás una ventana con 4 gráficas (una por cada canal EEG):
- **TP9** - Temporal izquierdo
- **AF7** - Frontal izquierdo
- **AF8** - Frontal derecho
- **TP10** - Temporal derecho

---

## 📊 Trabajar con el Stream EEG

### Opción A: Grabar datos a CSV

```bash
muselsl record --duration 60
```

Esto graba 60 segundos de datos EEG a un archivo CSV.

### Opción B: Acceder al stream desde Python

```python
from pylsl import StreamInlet, resolve_byprop
import numpy as np

# Buscar stream EEG
print("Buscando stream EEG...")
streams = resolve_byprop('type', 'EEG', timeout=10)

if not streams:
    print("No se encontró stream. ¿Está corriendo 'muselsl stream'?")
    exit()

# Conectar al stream
inlet = StreamInlet(streams[0])
info = inlet.info()

print(f"Conectado a: {info.name()}")
print(f"Frecuencia: {info.nominal_srate()} Hz")
print(f"Canales: {info.channel_count()}")

# Leer datos continuamente
while True:
    sample, timestamp = inlet.pull_sample()
    print(f"[{timestamp:.3f}] {np.array(sample)}")
```

### Opción C: Analizar bandas de frecuencia

```python
from pylsl import StreamInlet, resolve_byprop
import numpy as np
from scipy import signal

# Configuración
FS = 256  # Frecuencia de muestreo del Muse
WINDOW = 256  # 1 segundo de datos

# Bandas de frecuencia EEG
BANDS = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 50)
}

def get_band_power(data, fs, band):
    """Calcula la potencia en una banda de frecuencia."""
    low, high = band
    # Filtro butterworth
    b, a = signal.butter(4, [low/(fs/2), high/(fs/2)], btype='band')
    filtered = signal.filtfilt(b, a, data)
    return np.mean(filtered ** 2)

# Conectar al stream
streams = resolve_byprop('type', 'EEG', timeout=10)
inlet = StreamInlet(streams[0])

buffer = []

print("Analizando bandas de frecuencia...")
print("-" * 50)

while True:
    sample, _ = inlet.pull_sample()
    buffer.append(sample[0])  # Canal TP9
    
    if len(buffer) >= WINDOW:
        data = np.array(buffer[-WINDOW:])
        
        print("\nPotencia por banda (TP9):")
        for name, band in BANDS.items():
            power = get_band_power(data, FS, band)
            bar = "█" * int(power / 10)
            print(f"  {name:6s}: {power:8.2f} {bar}")
        
        buffer = buffer[-WINDOW//2:]  # Overlap 50%
```

---

## 🔧 Comandos Útiles de muselsl

| Comando | Descripción |
|---------|-------------|
| `muselsl list` | Buscar dispositivos Muse cercanos |
| `muselsl stream -a <MAC>` | Iniciar streaming EEG |
| `muselsl stream -a <MAC> -p` | Incluir datos PPG (ritmo cardíaco) |
| `muselsl stream -a <MAC> --acc` | Incluir acelerómetro |
| `muselsl stream -a <MAC> --gyro` | Incluir giroscopio |
| `muselsl record -d 60` | Grabar 60 segundos a CSV |
| `muselsl view` | Visualizar (requiere Tkinter) |

---

## 🐛 Solución de Problemas

### "Bluetooth device is turned off"
- Activa Bluetooth en Preferencias del Sistema → Bluetooth

### "No Muse devices found"
- Asegúrate de que la banda esté encendida (luz parpadeando)
- Acércala al computador
- Reinicia la banda (apagar/encender)
- Verifica que no esté conectada a otra app (Mind Monitor, Muse app)

### "No se encontró stream EEG"
- Primero ejecuta `muselsl stream` en otra terminal
- Espera a que diga "Streaming EEG..."

### Error de Tkinter con `muselsl view`
- Usa `python view_eeg.py` en su lugar (incluido en este repo)

### Señal ruidosa o plana
- Ajusta bien la banda en tu cabeza
- Humedece ligeramente los sensores
- Asegúrate de que los sensores de las orejas hagan buen contacto

### Desconexiones frecuentes
- Carga la banda completamente
- Reduce la distancia al computador
- Cierra otras apps que usen Bluetooth

---

## 📁 Estructura del Proyecto

```
eeg_muse_basic/
├── README.md           # Esta documentación
├── requirements.txt    # Dependencias Python
├── view_eeg.py         # Visualizador EEG (sin Tkinter)
└── examples/           # Scripts de ejemplo
    ├── record_eeg.py   # Grabar datos a CSV
    ├── analyze_bands.py # Análisis de bandas de frecuencia
    └── stream_basic.py # Ejemplo básico de lectura
```

---

## 📚 Recursos Adicionales

- [muselsl GitHub](https://github.com/alexandrebarachant/muse-lsl)
- [pylsl Documentation](https://labstreaminglayer.readthedocs.io/)
- [Muse Developer Resources](https://choosemuse.com/development/)

---

## 📄 Licencia

MIT License - Usa este código como quieras.
