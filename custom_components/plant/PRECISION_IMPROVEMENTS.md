# Sensor-Präzision Verbesserungen für homeassistant-brokkoli

## Problem
Lux- und Luftfeuchtigkeitssensoren zeigten zu viele Nachkommastellen an, was die Benutzerfreundlichkeit beeinträchtigte.

## Lösung Implementiert

### 1. Neue Precision Utils (`precision_utils.py`)
- **Zentrale Präzisionsverwaltung** für alle Sensortypen
- **Device-Class spezifische Rundung**
- **Display vs. Berechnung Präzision** Unterscheidung
- **PrecisionMixin** für einfache Integration

### 2. Sensor-Präzision Mappings

```python
SENSOR_PRECISION = {
    "illuminance": 0,        # 25000 lux (ohne Nachkommastellen)
    "humidity": 0,           # 65% (ohne Nachkommastellen)
    "temperature": 1,        # 20.5°C
    "moisture": 1,           # 45.5%
    "ppfd": 1,              # 250.5 µmol/m²/s
    "dli": 1,               # 15.2 mol/m²/d
    "conductivity": 0,       # 1500 µS/cm
    "co2": 0,               # 400 ppm
    "ph": 1,                # 6.5 pH
}
```

### 3. Aktualisierte Sensor-Klassen

#### PlantCurrentIlluminance
- **`suggested_display_precision = 0`** hinzugefügt
- **Automatische Rundung** in `state_changed()` und `async_update()`
- **Ganze Zahlen** für Lux-Werte (z.B. 25000 statt 25000.0)

#### PlantCurrentHumidity
- **`suggested_display_precision = 0`** hinzugefügt
- **Automatische Rundung** in `state_changed()` und `async_update()`
- **Ganze Zahlen** für Luftfeuchtigkeit (z.B. 65 statt 65.0)

#### PlantCurrentPpfd
- **`suggested_display_precision = 1`** hinzugefügt
- **1 Nachkommastelle** für PPFD-Werte (z.B. 250.5)

#### CycleMedianSensor
- **Individuelle Präzision** für jeden Sensor-Typ
- **0 Nachkommastellen** für Lux und Luftfeuchtigkeit
- **1 Nachkommastelle** für Temperatur, PPFD, DLI

### 4. Verbesserte Medianwert-Berechnung
In `__init__.py` wurde die Rundungslogik überarbeitet:

```python
# Alte Logik:
elif sensor_type in [\"temperature\", \"moisture\", \"humidity\", \"moisture_consumption\", \"CO2\"]:
    self._median_sensors[sensor_type] = round(value, 1)
else:  # conductivity, illuminance, fertilizer_consumption
    self._median_sensors[sensor_type] = round(value)

# Neue Logik:
elif sensor_type in [\"humidity\", \"illuminance\", \"CO2\", \"conductivity\"]:
    self._median_sensors[sensor_type] = round(value)  # Keine Nachkommastellen
elif sensor_type in [\"ppfd\", \"dli\"]:
    self._median_sensors[sensor_type] = round(value, 1)  # 1 Nachkommastelle
```

## Vorteile der Implementierung

### 1. **Bessere Benutzerfreundlichkeit**
- Lux-Werte: `25000` statt `25000.0000`
- Luftfeuchtigkeit: `65%` statt `65.000%`
- PPFD-Werte: `250.5` statt `250.5678`

### 2. **Home Assistant Standard-Konformität**
- Verwendet `suggested_display_precision` Attribut
- Folgt Home Assistant Best Practices
- Konsistent mit anderen Integrationen

### 3. **Erweiterbarkeit**
- Zentrale Konfiguration in `precision_utils.py`
- Einfache Anpassung für neue Sensor-Typen
- Trennung zwischen Display und Berechnungs-Präzision

### 4. **Performance**
- Reduzierte Datenübertragung
- Weniger Speicherbedarf in der Datenbank
- Schnellere UI-Darstellung

## Anwendung

### Für neue Sensoren
```python
from .precision_utils import PrecisionMixin, apply_sensor_precision

class NewSensor(PrecisionMixin, SensorEntity):
    def __init__(self, sensor_type: str, *args, **kwargs):
        super().__init__(sensor_type, *args, **kwargs)
        # Automatisch korrekte Präzision gesetzt
```

### Für bestehende Sensoren
```python
# Automatische Anwendung der Präzision
apply_sensor_precision(sensor, \"illuminance\")
```

## Testing

### Vor der Implementierung
- Lux: `25384.567890 lux`
- Luftfeuchtigkeit: `65.00000 %`
- PPFD: `250.567890 µmol/m²/s`

### Nach der Implementierung
- Lux: `25385 lux`
- Luftfeuchtigkeit: `65 %`
- PPFD: `250.6 µmol/m²/s`

## Migration

Die Änderungen sind **rückwärtskompatibel**:
- Bestehende Sensordaten bleiben erhalten
- Home Assistant erkennt automatisch die neue Präzision
- Keine manuellen Schritte erforderlich

## Wartung

Für zukünftige Anpassungen der Präzision:
1. Bearbeite `SENSOR_PRECISION` in `precision_utils.py`
2. Starte Home Assistant neu
3. Änderungen werden automatisch angewendet