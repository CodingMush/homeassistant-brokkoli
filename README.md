# Brokkoli Cannabis Management for Home Assistant

**The foundation of the Brokkoli Suite - Cannabis monitoring integration for Home Assistant**

A Home Assistant integration for monitoring cannabis plants with sensors and configurable thresholds. Part of the Brokkoli Suite for cannabis cultivation tracking.

## 🌱 Features / Funktionen

### Device-based Plant Management / Gerätebasierte Pflanzenverwaltung
- Cannabis plants as Home Assistant devices with grouped sensor entities / Cannabis-Pflanzen als Home Assistant-Geräte mit gruppierten Sensorentitäten
- Configurable thresholds for each sensor type / Konfigurierbare Schwellenwerte für jeden Sensortyp
- Problem state when sensor values exceed limits / Problemstatus, wenn Sensorwerte Grenzwerte überschreiten
- Individual plant helpers: health status, growing phase, flowering duration / Individuelle Pflanzenhelfer: Gesundheitsstatus, Wachstumsphase, Blütezeit
- Cycle system for grouping plants together / Zyklussystem zur Gruppierung von Pflanzen

### Supported Sensors / Unterstützte Sensoren
- **Moisture**: Soil moisture percentage / Bodenfeuchtigkeit in Prozent
- **Temperature**: Ambient temperature (°C/°F) / Umgebungstemperatur (°C/°F)
- **Light/Brightness**: Light intensity (lux) / Lichtintensität (Lux)
- **Conductivity**: Soil conductivity (µS/cm) / Bodenleitfähigkeit (µS/cm)
- **pH**: Soil pH level / Boden-pH-Wert
- **Humidity**: Air humidity percentage / Luftfeuchtigkeit in Prozent
- **Co2**: Air CO2 ppm / Luft-CO2 in ppm
- **Power**: Power consumption monitoring / Energieverbrauch-Überwachung
- **Daily Light Integral (DLI)**: Calculated from light sensors / Berechnet aus Lichtsensoren

### Seedfinder Integration
- Strain data fetching during setup / Sortendaten-Abruf während der Einrichtung
- Strain images and basic information / Sortenbilder und grundlegende Informationen
- Growth phase definitions / Definitionen der Wachstumsphasen

### Services & Configuration / Dienste & Konfiguration
- UI-based setup through config flow / UI-basierte Einrichtung über Config Flow
- Various services to interact with plants / Verschiedene Dienste zur Interaktion mit Pflanzen
- Sensor changes directly in plant configuration / Sensorwechsel direkt in der Pflanzenkonfiguration
- Automation triggers for dynamic sensor switching (e.g., room changes) / Automatisierungsauslöser für dynamischen Sensorwechsel (z.B. Raumwechsel)

## 🔧 Installation

### Prerequisites / Voraussetzungen
For the complete Brokkoli Suite, install these complementary components: / Für die vollständige Brokkoli-Suite installieren Sie diese ergänzenden Komponenten:

- **[Brokkoli Card](https://github.com/dingausmwald/lovelace-brokkoli-card)** - Lovelace cards for cannabis visualization / Lovelace-Karten für Cannabis-Visualisierung
- **[Seedfinder Integration](https://github.com/dingausmwald/homeassistant-seedfinder)** - Cannabis strain data and information / Cannabis-Sortendaten und -informationen

### HACS Installation (Recommended) / HACS-Installation (Empfohlen)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

1. Add this repository as a [Custom Repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS / Fügen Sie dieses Repository als [Custom Repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS hinzu
2. Set the category to "Integration" / Setzen Sie die Kategorie auf "Integration"
3. Click "Install" on the "Brokkoli Cannabis Management" card / Klicken Sie auf "Install" auf der "Brokkoli Cannabis Management"-Karte
4. Restart Home Assistant / Starten Sie Home Assistant neu

### Manual Installation / Manuelle Installation

1. Copy the `custom_components/plant/` directory to your `<config>/custom_components/` directory / Kopieren Sie das Verzeichnis `custom_components/plant/` in Ihr `<config>/custom_components/`-Verzeichnis
2. Restart Home Assistant / Starten Sie Home Assistant neu

## 🚀 Quick Start / Schnellstart

### 1. Set up your first cannabis plant / Richten Sie Ihre erste Cannabis-Pflanze ein
1. Go to **Settings** → **Devices & Services** → **Add Integration** / Gehen Sie zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**
2. Search for "Plant" and select it / Suchen Sie nach "Plant" und wählen Sie es aus
3. Follow the configuration flow to set up your cannabis plant / Folgen Sie dem Konfigurationsablauf, um Ihre Cannabis-Pflanze einzurichten
4. Assign your sensors (moisture, temperature, light, etc.) / Weisen Sie Ihre Sensoren zu (Feuchtigkeit, Temperatur, Licht usw.)

### 2. Configure thresholds / Konfigurieren Sie Schwellenwerte
- Each threshold (min/max values) becomes its own entity / Jeder Schwellenwert (Min/Max-Werte) wird zu einer eigenen Entität
- Adjust thresholds directly from the UI or via automations / Passen Sie Schwellenwerte direkt über die Benutzeroberfläche oder über Automatisierungen an
- Changes take effect immediately without restart / Änderungen treten sofort ohne Neustart in Kraft

### 3. Monitor and maintain / Überwachen und pflegen
- View all cannabis plants under **Settings** → **Devices & Services** → **Devices** / Zeigen Sie alle Cannabis-Pflanzen unter **Einstellungen** → **Geräte & Dienste** → **Geräte** an
- Check plant status and sensor readings / Überprüfen Sie den Pflanzenstatus und die Sensorwerte
- Monitor problem states when sensor values exceed thresholds / Überwachen Sie Problemzustände, wenn Sensorwerte Schwellenwerte überschreiten

## 📊 Sensor Management / Sensorverwaltung

Sensors can be changed directly in the plant's configuration interface or dynamically via automations when plants are moved between rooms. / Sensoren können direkt in der Konfigurationsoberfläche der Pflanze geändert oder dynamisch über Automatisierungen geändert werden, wenn Pflanzen zwischen Räumen verschoben werden.

## 🎪 Tent Management / Zeltverwaltung

The Brokkoli integration supports Tent entities for managing environmental sensors that can be assigned to multiple plants. / Die Brokkoli-Integration unterstützt Zelt-Entitäten zur Verwaltung von Umweltsensoren, die mehreren Pflanzen zugewiesen werden können.

### Tent Features / Zeltfunktionen
- Create and manage environmental sensor groups / Erstellen und verwalten Sie Umweltsensorgruppen
- Assign plants to tents for automatic sensor inheritance / Weisen Sie Pflanzen Zelten zu, um automatische Sensorvererbung zu erhalten
- Update tent sensors to automatically update all assigned plants / Aktualisieren Sie Zeltsensoren, um automatisch alle zugewiesenen Pflanzen zu aktualisieren

## 🎨 Brokkoli Suite Integration

Brokkoli Cannabis Management is the foundation of the Brokkoli Suite: / Brokkoli Cannabis Management ist die Grundlage der Brokkoli-Suite:

### [Brokkoli Card](https://github.com/dingausmwald/lovelace-brokkoli-card)
- Individual cannabis plant cards / Individuelle Cannabis-Pflanzenkarten
- Area cards for spatial plant arrangement / Bereichskarten für räumliche Pflanzenanordnung
- List cards for tabular overview / Listenkarten für tabellarische Übersicht
- Interactive plant positioning / Interaktive Pflanzenpositionierung

### [Seedfinder Integration](https://github.com/dingausmwald/homeassistant-seedfinder)
- Cannabis strain database access / Zugriff auf Cannabis-Sortendatenbank
- Strain data fetching during setup / Sortendaten-Abruf während der Einrichtung
- Strain imagery and basic information / Sortenbilder und grundlegende Informationen
- Growth phase definitions / Definitionen der Wachstumsphasen

## 🔧 Configuration / Konfiguration

### Problem Detection / Problemerkennung
Customize which sensor violations trigger problem states: / Passen Sie an, welche Sensorverletzungen Problemzustände auslösen:

1. Navigate to **Settings** → **Devices & Services** → **Plant Monitor** / Navigieren Sie zu **Einstellungen** → **Geräte & Dienste** → **Pflanzenmonitor**
2. Select your plant device / Wählen Sie Ihr Pflanzengerät aus
3. Click **Configure** / Klicken Sie auf **Konfigurieren**
4. Choose which threshold violations should trigger alerts / Wählen Sie aus, welche Schwellenwertverletzungen Warnungen auslösen sollen

### Strain Management / Sortenverwaltung
Update cannabis strain and refresh data from Seedfinder: / Aktualisieren Sie die Cannabis-Sorte und aktualisieren Sie Daten von Seedfinder:

1. Go to cannabis plant device configuration / Gehen Sie zur Konfiguration des Cannabis-Pflanzengeräts
2. Enter the exact strain name (Seedfinder PID format) / Geben Sie den genauen Sortennamen ein (Seedfinder PID-Format)
3. Enable "Force refresh" to update all data including images / Aktivieren Sie "Aktualisierung erzwingen", um alle Daten einschließlich Bilder zu aktualisieren
4. Strain changes take effect immediately / Sortenänderungen treten sofort in Kraft

### Central sensor decimals / Zentrale Sensorenachkommastellen
- Centralized defaults are defined in `custom_components/plant/sensor_configuration.py`. / Zentralisierte Standardeinstellungen sind in `custom_components/plant/sensor_configuration.py` definiert.
- The central config entry "Plant Monitor Konfiguration" exposes decimal options per sensor (e.g. `decimals_temperature`, `decimals_humidity`, `decimals_illuminance`, `decimals_ppfd`, `decimals_dli`, `decimals_total_water_consumption`, ...). / Der zentrale Konfigurationseintrag "Plant Monitor Konfiguration" zeigt Dezimaloptionen pro Sensor an (z.B. `decimals_temperature`, `decimals_humidity`, `decimals_illuminance`, `decimals_ppfd`, `decimals_dli`, `decimals_total_water_consumption`, ...).
- All live current sensors (temperature, humidity, illuminance, moisture, conductivity, CO2, ppfd, pH) and derived values use these settings for consistent rounding. / Alle Live-Current-Sensoren (Temperatur, Feuchtigkeit, Helligkeit, Bodenfeuchtigkeit, Leitfähigkeit, CO2, ppfd, pH) und abgeleitete Werte verwenden diese Einstellungen für konsistente Rundung.
- Manual updates (e.g. add watering) also respect the configured decimals. / Manuelle Aktualisierungen (z.B. Bewässerung hinzufügen) respektieren ebenfalls die konfigurierten Dezimalstellen.

## 📱 Available Services / Verfügbare Dienste

The integration provides various services to interact with your cannabis plants: / Die Integration bietet verschiedene Dienste zur Interaktion mit Ihren Cannabis-Pflanzen:

- `plant.replace_sensor` - Replace sensors for a plant / Sensoren für eine Pflanze ersetzen
- `plant.create_plant` - Create a new plant / Eine neue Pflanze erstellen
- `plant.remove_plant` - Remove a plant and all its entities / Eine Pflanze und alle ihre Entitäten entfernen
- `plant.clone_plant` - Create a clone/cutting of an existing plant / Einen Klon/Schnitt einer bestehenden Pflanze erstellen
- `plant.create_cycle` - Create a new cycle for grouping plants / Einen neuen Zyklus zur Gruppierung von Pflanzen erstellen
- `plant.remove_cycle` - Remove a cycle and all its entities / Einen Zyklus und alle seine Entitäten entfernen
- `plant.move_to_cycle` - Move plants to a cycle or remove from cycle / Pflanzen in einen Zyklus verschieben oder aus dem Zyklus entfernen
- `plant.update_plant_attributes` - Update plant attributes and information / Pflanzenattribute und -informationen aktualisieren
- `plant.move_to_area` - Move plants to different areas / Pflanzen in verschiedene Bereiche verschieben
- `plant.add_image` - Add images to plants / Bilder zu Pflanzen hinzufügen
- `plant.change_position` - Change plant position coordinates / Pflanzenpositions-Koordinaten ändern
- `plant.export_plants` - Export plant configurations / Pflanzenkonfigurationen exportieren
- `plant.import_plants` - Import plant configurations / Pflanzenkonfigurationen importieren
- `plant.create_tent` - Create a new tent for environmental sensors / Ein neues Zelt für Umweltsensoren erstellen
- `plant.change_tent` - Change tent assignment for a plant / Zeltzuweisung für eine Pflanze ändern
- `plant.update_tent_sensors` - Update sensors associated with a tent / Mit einem Zelt verknüpfte Sensoren aktualisieren

These services are integrated into the [Brokkoli Card](https://github.com/dingausmwald/lovelace-brokkoli-card) interface for convenient operation, or can be used directly in automations and scripts. / Diese Dienste sind in die [Brokkoli Card](https://github.com/dingausmwald/lovelace-brokkoli-card)-Oberfläche zur bequemen Bedienung integriert oder können direkt in Automatisierungen und Skripten verwendet werden.

## 🧪 Development and Testing / Entwicklung und Testen

For developers interested in contributing to the Brokkoli integration, comprehensive technical documentation is available in the [DEVELOPMENT.md](file:///d:/Python/2/homeassistant-brokkoli/DEVELOPMENT.md) file. This includes: / Für Entwickler, die zur Brokkoli-Integration beitragen möchten, ist umfassende technische Dokumentation in der Datei [DEVELOPMENT.md](file:///d:/Python/2/homeassistant-brokkoli/DEVELOPMENT.md) verfügbar. Diese enthält:

- Testing strategy and test organization / Teststrategie und Testorganisation
- Architecture overview / Architekturübersicht
- Development best practices / Entwicklungsbewährte Verfahren
- Quality metrics and troubleshooting tips / Qualitätsmetriken und Fehlerbehebungstipps

## 🆘 Troubleshooting / Fehlerbehebung

### Sensor Values Not Updating / Sensorwerte werden nicht aktualisiert
If old sensor values persist after cannabis plant reconfiguration: / Wenn alte Sensorwerte nach der Neu-Konfiguration der Cannabis-Pflanze bestehen bleiben:
- Use the `replace_sensor` service instead of removing/re-adding plants / Verwenden Sie den Dienst `replace_sensor` anstelle des Entfernens/Hinzufügens von Pflanzen

### Strain Not Found / Sorte nicht gefunden
- Ensure exact strain name matching Seedfinder PID format / Stellen Sie sicher, dass der genaue Sortenname dem Seedfinder PID-Format entspricht
- Check that Seedfinder integration is properly configured / Überprüfen Sie, ob die Seedfinder-Integration richtig konfiguriert ist

## 🤝 Contributing / Mitwirken

Contributions are welcome! Please feel free to submit pull requests, report issues, or suggest improvements. / Beiträge sind willkommen! Bitte senden Sie gerne Pull-Anfragen, melden Sie Probleme oder schlagen Sie Verbesserungen vor.

## 📄 License / Lizenz

This project is licensed under the MIT License. / Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## ☕ Support / Unterstützung

If you find this project helpful, consider supporting its development: / Wenn Sie dieses Projekt hilfreich finden, erwägen Sie, seine Entwicklung zu unterstützen:

<a href="https://buymeacoffee.com/dingausmwald" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 50px !important;">
</a>

---

**Part of the Brokkoli Suite** - Cannabis cultivation tracking for Home Assistant / **Teil der Brokkoli-Suite** - Cannabis-Kultivierungsverfolgung für Home Assistant