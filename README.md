# Navigation using GenAI

![Demo](https://github.com/bhumikakrishnamurthy/Navigation_using_GenAI/blob/main/output(1).jpeg)

## Overview
This is a Python web application that integrates Generative AI (Gemini API) with navigation and route optimization. It allows users to:
- Convert addresses into latitude and longitude using Gemini AI.
- Find optimized routes with fuel and pollution impact analysis.
- Visualize traffic congestion using a heatmap.
- Display route justifications (e.g., "16% fuel saved").

## Features
- **AI-powered Address Conversion**: Uses Gemini API to fetch lat/lng from addresses.
- **Traffic Heatmap**: Visualizes traffic congestion in a selected area.
- **Route Optimization**: Computes shortest routes using OpenRouteService.
- **Environmental Impact Analysis**: Calculates fuel saved and pollution reduced.

## Prerequisites
Ensure you have:
- **Python 3.x** installed on your system.
- Required dependencies installed (see below).

## Getting Started

## Steps to Use the Project

To use the Navigation_using_GenAIt, follow these steps:


1. Clone the GitHub project by running the following command in your terminal:
   ```bash
   git clone https://github.com/bhumikakrishnamurthy/Navigation_using_GenAI.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Navigation_using_GenAI
   ```

3. Install the required dependencies by running the following command:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the project by running the following command:
   ```bash
   python app.py
   ```

Open your web browser and go to http://localhost:5000 to access the application.

#### ``Now the project is up and running, ready to provide route predictions and traffic management capabilities based on the data and algorithms employed.``

---
***Note:*** *Before running the application, make sure you have the following:*

- *Python 3.x installed on your system.*

Configuration

-Update the following API keys in app.py before running:

   -Gemini API Key
   -OpenRouteService API Key
   -HERE Traffic API Key
   
-Usage

   -Enter the starting and destination addresses.
   -Choose your vehicle type (car, truck, cyclist, etc.).
   -Click "Find Route" to visualize:
   -The shortest route on the map.
   -Traffic congestion via a heatmap.
   -Fuel saved & pollution reduction.
---
### Traffic Heatmap:

Enter the starting and ending location in the input form.
Click the "Show EcoRouteMap" button to view the traffic congestion heatmap for the selected area.
Shortest Route:

Enter the starting and ending coordinates, select a vehicle type (car, bicycle, or foot) from the dropdown menu.
Click the "Find Shortest Route" button to display the shortest route on the map, along with the estimated duration in hours, minutes, and seconds.
License
This project is licensed under the MIT License. See the LICENSE file for details.
## About the Project

The Navigation_using_GenAI project aims to provide route prediction and traffic management capabilities using Python. It leverages various data sources, including historical traffic data, real-time traffic updates, and sensor data, to generate accurate predictions and optimize route recommendations.

The project's workflow involves several key steps:

1. **Data Gathering**: Relevant data is collected from multiple sources, such as traffic sensors, GPS devices, and historical traffic databases. This data provides valuable insights into traffic flow, congestion, road conditions, and other factors influencing route selection.

2. **Machine Learning Analysis**: Machine learning algorithms, such as deep learning models like LSTMs or graph convolutional networks (GCNs), are employed to analyze the collected data and generate predictions. These models learn patterns and relationships from historical data to predict future traffic conditions and route outcomes.

3. **Real-Time Updates Integration**: The predictions are combined with real-time traffic updates to further refine and adjust the recommended routes. This ensures that the system adapts to changing traffic conditions and provides the most accurate and up-to-date information to users.

4. **Visualization and User Interaction**: Interactive maps and data visualizations are utilized to visualize the results. Users can view predicted routes, traffic congestion levels, alternative routes, and estimated travel times. Real-time notifications or alerts about significant traffic incidents or changes may also be provided.


---
***Note:*** *The NAV_AI-Route-generator project is designed to be flexible and extensible, allowing for the integration of additional data sources, machine learning models, and visualization tools to enhance its capabilities.*

** ***``
Feel free to explore the project and leverage its features for optimizing your route planning and traffic management needs.
``*** **
