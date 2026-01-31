#!/usr/bin/env python3
"""
Grabar datos EEG a un archivo CSV

Requisitos:
- muselsl stream debe estar corriendo en otra terminal

Uso:
    python examples/record_eeg.py                    # Graba 60 segundos
    python examples/record_eeg.py --duration 120    # Graba 120 segundos
    python examples/record_eeg.py --output mi_sesion.csv
"""

import argparse
import csv
import time
from datetime import datetime
from pylsl import StreamInlet, resolve_byprop
import numpy as np

CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']

def main():
    parser = argparse.ArgumentParser(description='Grabar datos EEG a CSV')
    parser.add_argument('--duration', '-d', type=int, default=60,
                        help='Duración de la grabación en segundos (default: 60)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Nombre del archivo de salida (default: eeg_YYYYMMDD_HHMMSS.csv)')
    args = parser.parse_args()
    
    print("=" * 50)
    print("GRABADOR EEG - Guardar datos a CSV")
    print("=" * 50)
    print(f"\nDuración configurada: {args.duration} segundos")
    print("\nBuscando stream EEG...")
    
    streams = resolve_byprop('type', 'EEG', timeout=10)
    
    if not streams:
        print("\n❌ ERROR: No se encontró stream EEG.")
        print("   Asegúrate de ejecutar primero:")
        print("   muselsl stream --address <TU_MAC_ADDRESS>")
        return
    
    inlet = StreamInlet(streams[0])
    info = inlet.info()
    fs = int(info.nominal_srate())
    
    print(f"\n✅ Conectado a: {info.name()}")
    print(f"   Frecuencia: {fs} Hz")
    
    # Nombre del archivo
    if args.output:
        filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eeg_{timestamp}.csv"
    
    print(f"\n📁 Archivo de salida: {filename}")
    print("\n" + "-" * 50)
    print("Grabando... (Ctrl+C para detener antes)")
    print("-" * 50)
    
    samples_collected = 0
    total_samples = args.duration * fs
    start_time = time.time()
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp'] + CHANNELS)
            
            while samples_collected < total_samples:
                sample, timestamp = inlet.pull_sample()
                writer.writerow([timestamp] + list(sample[:4]))
                samples_collected += 1
                
                # Mostrar progreso cada segundo
                if samples_collected % fs == 0:
                    elapsed = time.time() - start_time
                    remaining = args.duration - elapsed
                    progress = (samples_collected / total_samples) * 100
                    print(f"\r  Progreso: {progress:5.1f}% | "
                          f"Tiempo restante: {remaining:5.1f}s | "
                          f"Muestras: {samples_collected}", end="")
        
        print(f"\n\n✅ Grabación completada!")
        print(f"   Archivo: {filename}")
        print(f"   Muestras: {samples_collected}")
        print(f"   Duración real: {time.time() - start_time:.1f}s")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Grabación detenida por el usuario")
        print(f"   Archivo: {filename}")
        print(f"   Muestras grabadas: {samples_collected}")

if __name__ == "__main__":
    main()
