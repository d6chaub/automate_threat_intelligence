import requests
import json

# Replace 'YOUR_API_KEY' with your actual API key
api_key = 'YOUR_API_KEY'

# Define the base URL for the API
base_url = 'https://api.recordedfuture.com/v2/alert/search'

# Set up headers with the API key
headers = {
    'X-RFToken': api_key,
    'Content-Type': 'application/json'
}

# Define the parameters for the request
params = {
    'fields': 'all',  # Specify the fields you want to retrieve
    'limit': 1000,    # The number of alerts to fetch per request (max limit may vary)
}

# Function to fetch alerts
def fetch_alerts():
    alerts = []
    offset = 0
    while True:
        # Add offset to params
        params['offset'] = offset

        # Make the API request
        response = requests.get(base_url, headers=headers, params=params)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f'Error: {response.status_code} - {response.text}')
            break

        data = response.json()

        # Check if there are alerts in the response
        if not data.get('data', {}).get('items'):
            break

        # Add the fetched alerts to the list
        alerts.extend(data['data']['items'])

        # Increment the offset
        offset += len(data['data']['items'])

        # Stop if fewer items than limit are returned, meaning we've reached the end
        if len(data['data']['items']) < params['limit']:
            break

    return alerts

# Fetch all alerts
alerts = fetch_alerts()

# Print the total number of alerts fetched
print(f'Total alerts fetched: {len(alerts)}')

# Save the alerts to a JSON file
with open('alerts.json', 'w') as f:
    json.dump(alerts, f, indent=4)

print('Alerts saved to alerts.json')
