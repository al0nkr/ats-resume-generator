import json
from datetime import datetime

def format_date(date_dict):
    """Format date from dictionary to string format"""
    if not date_dict:
        return ""
    month = str(date_dict.get('month', '')).zfill(2)
    year = str(date_dict.get('year', ''))
    return f"{month}/{year}"

def parse_document_content(data):
    """Parse document content from the XML-like structure"""
    try:
        # For direct JSON data without documents structure
        if isinstance(data, dict) and not data.get('documents'):
            return data

        # For data with documents structure
        if isinstance(data, dict) and data.get('documents'):
            for doc in data.get('documents', []):
                content = doc.get('document_content')
                if content:
                    # If content is already a dict, return it
                    if isinstance(content, dict):
                        return content
                    # If content is a string, try to parse it
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        continue
        
        print(f"Data structure received: {type(data)}")
        print("First level keys:", list(data.keys()) if isinstance(data, dict) else "Not a dict")
        
    except Exception as e:
        print(f"Error in parse_document_content: {str(e)}")
    return None

def categorize_skills(skill):
    """Dynamically categorize skills based on common patterns"""
    skill = skill.lower()
    
    patterns = {
        'Languages': ['python', 'java', 'javascript', 'c++', 'html', 'css', 'sql', 'dart', 'go', 'kotlin'],
        'Frameworks': ['react', 'flutter', 'express', 'django', 'flask', 'angular', 'vue'],
        'Developer Tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'postman', 'firebase'],
        'Libraries': ['numpy', 'pandas', 'tensorflow', 'pytorch', 'scipy', 'matplotlib']
    }
    
    for category, keywords in patterns.items():
        if any(keyword in skill for keyword in keywords):
            return category
            
    if 'db' in skill or 'database' in skill:
        return 'Developer Tools'
    if 'api' in skill:
        return 'Developer Tools'
    if '.js' in skill:
        return 'Libraries'
    
    return 'Others'

def create_resume_json(github_data, linkedin_data):
    """Create a structured resume JSON from GitHub and LinkedIn data"""
    
    # Basic Information
    basic_info = {
        "name": f"{linkedin_data.get('firstName', '')} {linkedin_data.get('lastName', '')}".strip(),
        "phone": "",  # Not available in provided data
        "email": github_data["basic_info"].get("email") or linkedin_data.get("email", ""),
        "linkedin": f"https://linkedin.com/in/{linkedin_data.get('public_id', '')}",
        "github": github_data["basic_info"].get("html_url", ""),
    }

    # Education
    education = []
    for edu in linkedin_data.get("education", []):
        education_entry = {
            "institution": edu.get("schoolName", ""),
            "location": edu.get("location", linkedin_data.get("locationName", "")),
            "degree": "",
            "date": f"{format_date(edu.get('timePeriod', {}).get('startDate'))} - {format_date(edu.get('timePeriod', {}).get('endDate'))}"
        }
        
        # Combine degree name and field of study if available
        degree_parts = []
        if edu.get("degreeName"):
            degree_parts.append(edu["degreeName"])
        if edu.get("fieldOfStudy"):
            degree_parts.append(edu["fieldOfStudy"])
        education_entry["degree"] = " - ".join(degree_parts)
        
        education.append(education_entry)

    # Experience
    experience = []
    for exp in linkedin_data.get("experience", []):
        exp_entry = {
            "title": exp.get("title", ""),
            "company": exp.get("companyName", ""),
            "location": exp.get("locationName", linkedin_data.get("locationName", "")),
            "date": f"{format_date(exp.get('timePeriod', {}).get('startDate'))} - {format_date(exp.get('timePeriod', {}).get('endDate'))}",
            "bullets": []
        }
        
        # Add summary as bullet point if available
        if exp.get("description"):
            exp_entry["bullets"].append(exp["description"])
            
        experience.append(exp_entry)

    # Projects
    projects = []
    for repo in github_data.get("repositories", []):
        if repo.get("description") or repo.get("name"):  # Include all meaningful projects
            project = {
                "name": repo.get("name", ""),
                "technologies": repo.get("language", ""),
                "bullets": []
            }
            
            if repo.get("description"):
                project["bullets"].append(repo["description"])
            if repo.get("stars") > 0:
                project["bullets"].append(f"Received {repo['stars']} stars on GitHub")
            if repo.get("forks") > 0:
                project["bullets"].append(f"Project forked {repo['forks']} times")
                
            projects.append(project)

    # Skills
    skills_set = set()
    
    # From LinkedIn
    for skill in linkedin_data.get("skills", []):
        if skill.get("name"):
            # Split composite skills
            skill_parts = skill["name"].split(" · ")
            skills_set.update(skill_parts)
    
    # From GitHub languages
    for lang in github_data.get("languages", {}):
        skills_set.add(lang)

    # Categorize skills
    categorized_skills = {}
    for skill in skills_set:
        category = categorize_skills(skill)
        if category not in categorized_skills:
            categorized_skills[category] = []
        categorized_skills[category].append(skill)

    # Final resume structure
    resume_data = {
        **basic_info,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": categorized_skills
    }

    return resume_data

def main():
    try:
        # Read JSON files
        print("Reading files...")
        with open('github.json', 'r', encoding='utf-8') as f:
            github_raw = json.load(f)
            print("GitHub file loaded successfully")
        
        with open('linkedin.json', 'r', encoding='utf-8') as f:
            linkedin_raw = json.load(f)
            print("LinkedIn file loaded successfully")
        
        # Parse document content
        print("\nParsing document content...")
        github_data = parse_document_content(github_raw)
        print("GitHub data parsed:", bool(github_data))
        if not github_data:
            print("GitHub data structure:", type(github_raw))
            
        linkedin_data = parse_document_content(linkedin_raw)
        print("LinkedIn data parsed:", bool(linkedin_data))
        if not linkedin_data:
            print("LinkedIn data structure:", type(linkedin_raw))
        
        if not github_data or not linkedin_data:
            raise ValueError("Could not parse document content from one or both files")
        
        # Create resume JSON
        print("\nCreating resume JSON...")
        resume_json = create_resume_json(github_data, linkedin_data)
        
        # Save to file
        print("\nSaving resume JSON...")
        with open('resume.json', 'w', encoding='utf-8') as f:
            json.dump(resume_json, f, indent=4, ensure_ascii=False)
            
        print("Resume JSON file created successfully!")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("\nFull error traceback:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()