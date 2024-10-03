import requests
import phonenumbers
from colorama import Fore, init
import json
import base64

# Initialize colorama
init(autoreset=True)

def display_logo():
    logo = f"""
    {Fore.GREEN}######################################
    #                                    #
    #   {Fore.CYAN}PHONE LOOKUP TOOL{Fore.GREEN}              #
    #                                    #
    ######################################
    {Fore.YELLOW}       
    """
    print(logo)

def save_results(phone_number, data):
    filename = f"lookup_{phone_number}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"{Fore.CYAN}Results saved to {filename}")

def lookup_phone_number(phone_number, api_key, geocode_api_key, provider='Numverify'):
    # Validate and format the phone number
    try:
        parsed_number = phonenumbers.parse(phone_number)
        if not phonenumbers.is_valid_number(parsed_number):
            print(f"{Fore.RED}The phone number is not valid.")
            return
        
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        print(f"{Fore.CYAN}Formatted Phone Number: {Fore.WHITE}{formatted_number}")

        if provider == 'Numverify':
            GEO_API_URL = f"http://apilayer.net/api/validate?access_key={api_key}&number={formatted_number}"
        else:
            print(f"{Fore.RED}Unknown provider: {provider}")
            return

        # Fetch additional location information from the selected API
        response = requests.get(GEO_API_URL)

        # Print raw response for debugging
        print(f"{Fore.YELLOW}Raw response: {response.text}")
        print(f"{Fore.YELLOW}Response headers: {response.headers}")

        # Check response content type and decode JSON if available
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    data = response.json()
                    if data.get('valid'):
                        result = {
                            "Username": data.get('username', 'Not available'),
                            "Sex": data.get('sex', 'Not available'),
                            "Location": data.get('location', 'Not available'),
                            "Carrier": data.get('carrier', 'Not available'),
                            "Country Code": data.get('country_code', 'Not available'),
                            "Country Name": data.get('country_name', 'Not available'),
                            "Line Type": data.get('line_type', 'Not available')
                        }

                        # Fetch Latitude and Longitude using Geocoding API
                        if result["Location"] != 'Not available':
                            geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={result['Location']}&key={geocode_api_key}"
                            geocode_response = requests.get(geocode_url)
                            if geocode_response.status_code == 200:
                                geocode_data = geocode_response.json()
                                if geocode_data['results']:
                                    lat_lng = geocode_data['results'][0]['geometry']
                                    result['Latitude'] = lat_lng.get('lat', 'Not available')
                                    result['Longitude'] = lat_lng.get('lng', 'Not available')
                                    print(f"{Fore.CYAN}Latitude: {Fore.WHITE}{result['Latitude']}")
                                    print(f"{Fore.CYAN}Longitude: {Fore.WHITE}{result['Longitude']}")
                                else:
                                    print(f"{Fore.RED}Could not retrieve latitude and longitude.")
                            else:
                                print(f"{Fore.RED}Geocoding API request failed with status code: {geocode_response.status_code}")
                        
                        for key, value in result.items():
                            print(f"{Fore.CYAN}{key}: {Fore.WHITE}{value}")
                        save_results(formatted_number, result)
                    else:
                        print(f"{Fore.RED}Detailed location information not available. Reason: {data.get('error', {}).get('info', 'No error message provided')}")
                except ValueError:
                    print(f"{Fore.RED}Error decoding JSON response.")
            else:
                print(f"{Fore.RED}Unexpected content type: {response.headers.get('Content-Type')}")
        else:
            print(f"{Fore.RED}Failed to retrieve data. Status code: {response.status_code}")
            try:
                data = response.json()
                print(f"{Fore.RED}Error message: {data.get('error', {}).get('info', 'No error message provided')}")
            except ValueError:
                print(f"{Fore.RED}Unable to parse error message.")
    
    except phonenumbers.phonenumberutil.NumberParseException:
        print(f"{Fore.RED}Invalid phone number format. Please try again.")
    except requests.RequestException as e:
        print(f"{Fore.RED}Error fetching location data: {e}")
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}")

def main():
    display_logo()
    
    # Prompt user for API keys
    api_key = input(f"{Fore.YELLOW}Enter your Numverify API key: {Fore.WHITE}")
    geocode_api_key = input(f"{Fore.YELLOW}Enter your OpenCage Geocoding API key: {Fore.WHITE}")
    
    while True:
        print(f"\n{Fore.BLUE}Phone Number Information Lookup")
        print(f"{Fore.GREEN}1. Lookup a Phone Number")
        print(f"{Fore.GREEN}2. Change API Provider")
        print(f"{Fore.RED}3. Exit")

        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Fore.WHITE}")

        if choice == '1':
            phone_number = input(f"{Fore.YELLOW}Enter phone number (e.g., +11234567890): {Fore.WHITE}")
            lookup_phone_number(phone_number, api_key, geocode_api_key)
        elif choice == '2':
            print(f"{Fore.CYAN}Currently supported providers: Numverify")
            # You can add more providers here in the future
        elif choice == '3':
            print(f"{Fore.RED}Exiting the program.")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
