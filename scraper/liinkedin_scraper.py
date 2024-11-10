


from linkedin_api import Linkedin
import json
import re

def extract_username(input_text):
    """
    Extract LinkedIn username from either username or full profile URL
    """
    # Check if input is a URL
    if 'linkedin.com/in/' in input_text:
        # Extract username from URL
        username = input_text.split('linkedin.com/in/')[-1].split('/')[0]
        # Remove any trailing parameters
        username = username.split('?')[0]
    else:
        # Assume it's already a username
        username = input_text.strip()
    
    # Remove any special characters
    username = re.sub(r'[^a-zA-Z0-9\-]', '', username)
    return username

def get_linkedin_data(email, password, profile_identifier):
    """
    Get LinkedIn profile data using either username or profile URL
    
    Args:
        email (str): LinkedIn login email
        password (str): LinkedIn login password
        profile_identifier (str): Either username or full profile URL
    """
    try:
        # Extract username
        username = extract_username(profile_identifier)
        
        # Initialize API
        api = Linkedin(email, password)
        
        # Get profile data
        profile_data = api.get_profile(username)
        
        if profile_data:
            # Save to file
            filename = f'{username}_linkedin_data.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
            print(f"Data saved to {filename}")
            
            # Print basic info
            print("\nBasic Information:")
            print(f"Name: {profile_data.get('firstName', '')} {profile_data.get('lastName', '')}")
            print(f"Headline: {profile_data.get('headline', '')}")
            print(f"Location: {profile_data.get('locationName', '')}")
            
            return profile_data
        else:
            print(f"No data found for username: {username}")
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    email = input("Enter your LinkedIn email: ")
    password = input("Enter your LinkedIn password: ")
    
    while True:
        profile_input = input("\nEnter LinkedIn username or full profile URL (or 'quit' to exit): ")
        
        if profile_input.lower() == 'quit':
            break
            
        data = get_linkedin_data(email, password, profile_input)
        
        # Ask if user wants to scrape another profile
        if input("\nScrape another profile? (y/n): ").lower() != 'y':
            break

print("Program finished.")