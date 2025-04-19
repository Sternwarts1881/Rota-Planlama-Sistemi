# Route Planning System

![WhatsApp Image 2025-04-19 at 19 17 46](https://github.com/user-attachments/assets/4a4067bb-bb4c-446b-8a30-29e0a7286b9f)


**Description**

This project is a route planning application developed for the Programming Laboratory II course at Kocaeli University. It uses Python 3, PyQt5, and Folium to provide a graphical user interface (GUI) and an interactive map for calculating transit (bus, tram) and taxi routes.

---

## Features

- **Standard Route**: Calculates the optimal path based on weighted scores for distance, time, and cost.
- **Least Stops Route**: Finds the shortest route by minimizing the number of stops.
- **Taxi Route**: Uses walking for distances under 3 km and a taxi fare/time estimate for longer trips.
- **Other Alternative Routes**: Multiple routes favoring different vehicle types.
- **Payment Method**: Allows users to add and manage their preferred payment methods (e.g. credit cards, cash) for paying fares.
- **Special Day Discount**: Applies discounts on bus and tram fares for special days.
- **PyQt5 GUI**: Enter start/end coordinates, select vehicle type and discount mode, then click **Calculate**.
- **Interactive Map**: Displays stops and routes on a Folium map embedded via QWebEngineView.

---

## Requirements

- Python 3.7 or higher
- Python packages:
  - `PyQt5`
  - `PyQtWebEngine`
  - `folium`

It is recommended to run in a virtual environment.

---

## Directory Structure

```
Rota-Planlama-Sistemi/
├── App.py                  # Main application code
├── veriseti.json           # Transit stops and connections data
├── map.html                # Generated map file (ignored by Git)
├── PROGRAMLAMA...-Rapor-1.pdf  # Project report (ignored by Git)
├── appIcon.png             # Application icon
├── busIcon.png             # Bus icon
├── tramIcon.png            # Tram icon
├── README.md               # Project documentation (this file)
└── .gitignore              # Excludes map.html and PDF from tracking
```

> **Note:** `map.html` and the project report PDF are excluded via `.gitignore` and will not appear in the repository.

---

## Key Classes & Modules

- **DistanceCalculator**: Computes distances using the Haversine formula.
- **Location, Stop, Transfer**: Represent map stops and transfer details.
- **Passenger**: Models passenger behavior, discount eligibility, and walking time.
- **Vehicle**: Abstract class with `Bus`, `Tram`, and `Taxi` implementations.
- **StopLoader**: Loads stop data from `veriseti.json`.
- **RouteLogic**: Defines routing algorithms (`bellmanFord_Standard`, `bellmanFord_LeastStops`, `TaxiRouteLogic`).
- **RoutePlanner**: Integrates walking or taxi for the first/last mile.
- **UI_Data**: Holds shared data structures for vehicles and routes.
- **MainWindow**: Builds the PyQt5 GUI and manages user actions and map rendering.

---

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.


