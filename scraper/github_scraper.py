import requests
import json
from datetime import datetime

class GitHubPublicScraper:
    def __init__(self):
        self.base_url = 'https://api.github.com'

    def get_user_profile(self, username):
        """Get basic user profile information"""
        response = requests.get(f'{self.base_url}/users/{username}')
        if response.status_code == 200:
            return response.json()
        return None

    def get_repositories(self, username):
        """Get all public repositories of a user"""
        repos = []
        page = 1
        
        while True:
            response = requests.get(
                f'{self.base_url}/users/{username}/repos',
                params={'page': page, 'per_page': 100}
            )
            
            if response.status_code != 200 or not response.json():
                break
                
            current_repos = response.json()
            repos.extend([{
                'name': repo['name'],
                'description': repo['description'],
                'language': repo['language'],
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'last_updated': repo['updated_at']
            } for repo in current_repos])
            
            page += 1
            
            # Basic rate limit handling
            if response.headers.get('X-RateLimit-Remaining') == '0':
                print("Rate limit reached. Please wait or use an access token.")
                break
                
        return repos

    def get_profile_readme(self, username):
        """Get profile README.md content if it exists"""
        response = requests.get(
            f'{self.base_url}/repos/{username}/{username}/readme',
            headers={'Accept': 'application/vnd.github.raw'}
        )
        if response.status_code == 200:
            return response.text
        return None

    def get_languages_used(self, username):
        """Get languages used across all repositories"""
        repos = self.get_repositories(username)
        languages = {}
        
        for repo in repos:
            if repo['language']:
                languages[repo['language']] = languages.get(repo['language'], 0) + 1
                
        return languages

def save_github_data(username):
    """Save all public GitHub data for a user"""
    scraper = GitHubPublicScraper()
    
    # Collect all data
    profile_data = {
        'basic_info': scraper.get_user_profile(username),
        'repositories': scraper.get_repositories(username),
        'languages': scraper.get_languages_used(username),
        'profile_readme': scraper.get_profile_readme(username),
        'scraped_at': datetime.now().isoformat()
    }
    
    # Save to file
    filename = f'{username}_github_data.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2)
    
    return filename

# Example usage
if __name__ == "__main__":
    username = "MISHRA-TUSHAR"  
    try:
        output_file = save_github_data(username)
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")