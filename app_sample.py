import folium
from folium.plugins import HeatMap
import requests
from flask import Flask, render_template, request
from folium import PolyLine
import openrouteservice
import herepy

import google.generativeai as genai

genai.configure(api_key="AIzaSyD0pySyekLZ2yrSoIvfMDkqdG-9hoFuq0s")

def get_coordinates(address):
    model = genai.GenerativeModel("gemini-pro")  # Use the correct model
    prompt = f"Provide the latitude and longitude for this address: {address} in the format lat, lng"
    response = model.generate_content(prompt)  # Correct function
    return response.text.strip() if response.text else None

def get_coordinates_osm(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
    response = requests.get(url).json()
    if response:
        return f"{response[0]['lat']}, {response[0]['lon']}"
    return None

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

def calculate_route_impact(distance, vehicle_type):
    baseline_distance = 5  # Assume shortest route possible

    if distance <= 0:  # Prevent invalid values
        return 0, 0  

    # Compare with a reasonable baseline
    fuel_saved = max(0, round((1 - distance / (distance + baseline_distance)) * 100, 2))
    pollution_reduction = max(0, round((fuel_saved * 0.8), 2))

    return fuel_saved, pollution_reduction






def get_route_distance(lat1, lng1, lat2, lng2, vehicle_type):
    api_key = "5b3ce3597851110001cf62484043ec17e186496fb57eb4c79240cb45"
    url = f"https://api.openrouteservice.org/v2/directions/{vehicle_type}/geojson"

    body = {
        "coordinates": [[lng1, lat1], [lng2, lat2]]
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)  # Print full API response

        try:
            distance = data['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert meters to km
            print(f"Extracted Route Distance: {distance} km")  # Debug print
            return distance
        except (KeyError, IndexError):
            print("Error parsing route distance:", data)
            return 0  # Return 0 if parsing fails
    else:
        print("API Error:", response.status_code, response.json())
        return 0  # Return 0 if API call fails





@app.route('/', methods=['POST', 'GET'])
def get_map():
    map_html = None
    formatted_duration = "" 
    justification = ""
    if request.method == 'POST':
        start_address = request.form['start']
        end_address = request.form['end']
        vehicle_type = request.form['vehicle_type']
        


        # Convert addresses to lat/lng using Gemini API
        start_coords = get_coordinates(start_address)  # Returns "lat, lng"
        end_coords = get_coordinates(end_address)  # Returns "lat, lng"

        lat1, lng1 = map(float, start_coords.split(','))
        lat2, lng2 = map(float, end_coords.split(','))



        distance = get_route_distance(lat1, lng1, lat2, lng2, vehicle_type)  # Fetch distance
        fuel_saved, pollution_reduction = calculate_route_impact(distance, vehicle_type)
        

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
        if vehicle_type == 'driving-car':
            profile = 'driving-car'
        elif vehicle_type == 'driving-hgv':
            profile = 'driving-hgv'

        elif vehicle_type == 'cycling-electric':
            profile = 'cycling-electric'
        elif vehicle_type == 'cycling-regular':
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

        justification = f"{fuel_saved}% fuel saved, {pollution_reduction}% less pollution"



        print(f"Start coords: {lat1}, {lng1}")
        print(f"End coords: {lat2}, {lng2}")
        print(f"Vehicle Type: {vehicle_type}")
        print(f"Distance from API: {distance} km")
        print(f"Fuel saved: {fuel_saved}%")
        print(f"Pollution reduction: {pollution_reduction}%")


    return render_template('index.html', map_html=map_html, duration=formatted_duration, justification=justification)

if __name__ == '__main__':
    app.run(debug=True) 
