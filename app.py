import folium
from folium.plugins import HeatMap
import requests
from flask import Flask, render_template, request
from folium import PolyLine
import openrouteservice
import herepy

import google.generativeai as genai

genai.configure(api_key="AIzaSyBPG9pMEfbOVWMp6fJLLfoHyf_g8xU5m-M")

def get_coordinates(address):
    model = genai.GenerativeModel("gemini-pro")  # Use the correct model
    prompt = f"Provide the latitude and longitude for this address: {address} in the format lat, lng"
    response = model.generate_content(prompt)  # Correct function
    return response.text.strip() if response.text else None



app = Flask(__name__, template_folder='template')


def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def validate_bbox(lat1, lng1, lat2, lng2):
    # Ensure lat1, lng1 are southwest and lat2, lng2 are northeast
    sw_lat = min(lat1, lat2)
    sw_lng = min(lng1, lng2)
    ne_lat = max(lat1, lat2)
    ne_lng = max(lng1, lng2)
    return sw_lat, sw_lng, ne_lat, ne_lng




@app.route('/', methods=['POST', 'GET'])
def get_map():
    map_html = None
    formatted_duration = "" 
    if request.method == 'POST':
        start_address = request.form['start']
        end_address = request.form['end']
        vehicle_type = request.form['vehicle_type']

        # Convert addresses to lat/lng using Gemini API
        start_coords = get_coordinates(start_address)  # Returns "lat, lng"
        end_coords = get_coordinates(end_address)  # Returns "lat, lng"

        lat1, lng1 = map(float, start_coords.split(','))
        lat2, lng2 = map(float, end_coords.split(','))

        # lat1 = float(request.form['lat1'])
        # lng1 = float(request.form['lng1'])
        # lat2 = float(request.form['lat2'])
        # lng2 = float(request.form['lng2'])
        # vehicle_type = request.form['vehicle_type']

         # Validate and adjust bounding box
        sw_lat, sw_lng, ne_lat, ne_lng = validate_bbox(lat1, lng1, lat2, lng2)


        url = f"https://data.traffic.hereapi.com/v7/flow?locationReferencing=shape&in=bbox:{sw_lng},{sw_lat},{ne_lng},{ne_lat}&apiKey=xJZG4uIwHrDKg5Qq9Eb0lGz0OvZAGiDz1SpuOfcrFbs"

    
        print(url)

        response = requests.get(url)
        traffic_data = response.json()
        print(traffic_data)

        # Process the traffic_data and create a list of coordinates for the heatmap
        coordinates = []
        response = requests.get(url)
        traffic_data = response.json()

        # Use .get() to safely access 'results'
        results = traffic_data.get('results', [])

        if not results:
            print("No results found in traffic data.")
            # Handle the case where there are no results
            # For example, you could return an empty list or a default value
            coordinates = []  # or handle it in a way that makes sense for your application
        else:
            # If results are found, process them as before
            for result in results:
                for link in result['location']['shape']['links']:
                    for point in link['points']:
                        coordinates.append((point['lat'], point['lng']))

        # Create a map centered at the average of the input coordinates
        m = folium.Map(location=[(float(lat1) + float(lat2))/2, (float(lng1) + float(lng2))/2], zoom_start=14)

        # Add a heatmap layer to the map using the coordinates
        HeatMap(coordinates).add_to(m)
        client = openrouteservice.Client(key='5b3ce3597851110001cf62484043ec17e186496fb57eb4c79240cb45')  # Replace with your OpenRouteService API key
        coords = [[lng1, lat1], [lng2, lat2]]
        
        # Set the profile based on the vehicle type
        if vehicle_type == 'car':
            profile = 'driving-car'
        elif vehicle_type == 'Truck':
            profile = 'driving-hgv'
            
        elif vehicle_type == 'electric':
            profile = 'cycling-electric'
        elif vehicle_type == 'cyclist':
            profile = 'cycling-regular'
            
        else:
            profile = 'foot-walking'




        # Find the shortest path using OpenRouteService
        route = client.directions(coordinates=coords, profile=profile, format='geojson')
        duration = route['features'][0]['properties']['segments'][0]['duration']  # Get the duration in seconds
        
        # Add the shortest path to the map
        folium.GeoJson(route, name='Shortest Path').add_to(m)

        # Add start and end markers to the map
        folium.Marker([lat1, lng1], popup='Start', icon=folium.Icon(color='green', icon='play')).add_to(m)
        folium.Marker([lat2, lng2], popup='End', icon=folium.Icon(color='red', icon='stop')).add_to(m)

        map_html = m._repr_html_()
        formatted_duration = format_duration(duration)
    return render_template('index.html', map_html=map_html, duration=formatted_duration)

if __name__ == '__main__':
    app.run(debug=True)