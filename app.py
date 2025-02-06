import folium
from folium.plugins import HeatMap
import requests
from flask import Flask, render_template, request
from folium import PolyLine
import openrouteservice
import herepy
import requests
from flask import Flask, request, jsonify

import google.generativeai as genai

genai.configure(api_key="AIzaSyD0pySyekLZ2yrSoIvfMDkqdG-9hoFuq0s")

def get_coordinates(address):
    model = genai.GenerativeModel("gemini-pro")  # Use the correct model
    prompt = f"Provide the exact latitude and longitude for this address: {address} in the format lat, lng"
    response = model.generate_content(prompt)  # Correct function
    return response.text.strip() if response.text else None



def get_coordinates_osm(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
    
    headers = {
        "User-Agent": "NavigationApp/1.0"
    }

    print(f"Sending request to: {url}")  # Debugging step

    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Response Status Code: {response.status_code}")  # Debugging step
        print(f"Response Text: {response.text[:500]}")  # Print first 500 chars of response

        response.raise_for_status()  # Raise an error if status is not 200 OK

        if not response.text.strip():
            print("Error: Empty response from API")
            return None

        data = response.json()
        if not data:
            print("Error: No results found for the address")
            return None

        print(f"Coordinates Found: {data[0]['lat']}, {data[0]['lon']}")  # Debugging step
        return f"{data[0]['lat']}, {data[0]['lon']}"

    except requests.exceptions.JSONDecodeError:
        print(f"Error: Could not decode JSON. Response text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed - {e}")
    
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
    distance_estimated=""

    if request.method == 'POST':
        start_address = request.form['start']
        end_address = request.form['end']
        vehicle_type = request.form['vehicle_type']

        # Convert addresses to lat/lng
        start_coords = get_coordinates_osm(start_address)  
        end_coords = get_coordinates_osm(end_address)  

        if not start_coords or not end_coords:
            return jsonify({"error": "Could not retrieve coordinates"}), 500  

        lat1, lng1 = map(float, start_coords.split(','))
        lat2, lng2 = map(float, end_coords.split(','))

        # Validate vehicle type
        valid_profiles = {'driving-car', 'driving-hgv', 'cycling-electric', 'cycling-regular', 'foot-walking'}
        if vehicle_type not in valid_profiles:
            print(f"Invalid vehicle type: {vehicle_type}. Defaulting to walking.")
            vehicle_type = 'foot-walking'  

        # Calculate route distance & impact
        distance = get_route_distance(lat1, lng1, lat2, lng2, vehicle_type)  
        fuel_saved, pollution_reduction = calculate_route_impact(distance, vehicle_type)

        # Validate and adjust bounding box
        sw_lat, sw_lng, ne_lat, ne_lng = validate_bbox(lat1, lng1, lat2, lng2)

        # Get traffic data
        url = f"https://data.traffic.hereapi.com/v7/flow?locationReferencing=shape&in=bbox:{sw_lng},{sw_lat},{ne_lng},{ne_lat}&apiKey=xJZG4uIwHrDKg5Qq9Eb0lGz0OvZAGiDz1SpuOfcrFbs"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching traffic data: {response.status_code}")
            return jsonify({"error": "Traffic data request failed"}), 500

        traffic_data = response.json()
        results = traffic_data.get('results', [])  

        coordinates = []
        if results:
            for result in results:
                for link in result.get('location', {}).get('shape', {}).get('links', []):
                    for point in link.get('points', []):
                        coordinates.append((point['lat'], point['lng']))

        # Create a map centered at the midpoint
        m = folium.Map(location=[(lat1 + lat2) / 2, (lng1 + lng2) / 2], zoom_start=14)
        HeatMap(coordinates).add_to(m)

        # OpenRouteService Request
        client = openrouteservice.Client(key="5b3ce3597851110001cf62484043ec17e186496fb57eb4c79240cb45")  
        coords = [[lng1, lat1], [lng2, lat2]]

        try:
            route = client.directions(coordinates=coords, profile=vehicle_type, format='geojson')
            duration = route['features'][0]['properties']['segments'][0]['duration']  
        except Exception as e:
            print(f"Error fetching route from OpenRouteService: {e}")
            return jsonify({"error": "Failed to get route"}), 500

        # Add route to map
        folium.GeoJson(route, name='Shortest Path').add_to(m)
        folium.Marker([lat1, lng1], popup='Start', icon=folium.Icon(color='green', icon='play')).add_to(m)
        folium.Marker([lat2, lng2], popup='End', icon=folium.Icon(color='red', icon='stop')).add_to(m)

        map_html = m._repr_html_()
        formatted_duration = format_duration(duration)
        justification = f"{fuel_saved}% fuel saved, {pollution_reduction}% less pollution"
        
        print(f"Start: {lat1}, {lng1} | End: {lat2}, {lng2} | Vehicle: {vehicle_type}")
        print(f"Distance: {distance} km | Fuel Saved: {fuel_saved}% | Pollution Reduction: {pollution_reduction}%")

    return render_template('index.html', map_html=map_html, duration=formatted_duration, justification=justification)

if __name__ == '__main__':
    app.run(debug=True) 




