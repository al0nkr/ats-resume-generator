import json
from datetime import datetime, timezone

def process_json_files(github_data, linkedin_data):
    # Initialize the consolidated data structure in the required format
    consolidated_data = {
        "name": github_data["basic_info"]["name"],
        "address": ["India"],
        "contact": {
            "email": github_data["basic_info"]["email"],
            "phone": ""
        },
        "websites": [
            {
                "text": "GitHub",
                "url": github_data["basic_info"]["html_url"],
                "icon": "github"
            },
            {
                "text": "LinkedIn",
                "url": f"https://linkedin.com/in/{linkedin_data['public_id']}",
                "icon": "linkedin"
            }
        ],
        "summary": linkedin_data.get("summary", ""),
        "education": [],
        "experiences": [],
        "projects": [],
        "skills": []
    }
    
    # Process education section
    for edu in linkedin_data["education"]:
        education_entry = {
            "school": edu["schoolName"],
            "degrees": [
                {
                    "names": [edu.get("degreeName", "")],
                    "startdate": f"{edu['timePeriod']['startDate']['year']}-{edu['timePeriod']['startDate'].get('month', 1):02d}",
                    "enddate": f"{edu['timePeriod']['endDate']['year']}-{edu['timePeriod']['endDate'].get('month', 12):02d}" if "endDate" in edu["timePeriod"] else "Present",
                    "gpa": ""
                }
            ],
            "achievements": []
        }
        consolidated_data["education"].append(education_entry)
    
    # Process experience section
    for exp in linkedin_data["experience"]:
        experience_entry = {
            "company": exp["companyName"],
            "titles": [
                {
                    "name": exp["title"],
                    "startdate": f"{exp['timePeriod']['startDate']['year']}-{exp['timePeriod']['startDate'].get('month', 1):02d}",
                    "enddate": f"{exp['timePeriod']['endDate']['year']}-{exp['timePeriod']['endDate'].get('month', 12):02d}" if "endDate" in exp["timePeriod"] else None
                }
            ],
            "highlights": []
        }
        consolidated_data["experiences"].append(experience_entry)
    
    # Process projects from GitHub data
    for project in github_data["repositories"]:
        if project["description"]:  # Only include projects with descriptions
            project_entry = {
                "name": project["name"],
                "description": project["description"]
            }
            consolidated_data["projects"].append(project_entry)
    
    # Process skills section
    technical_skills = set()
    for language in github_data["languages"].keys():
        technical_skills.add(language)
    for skill in linkedin_data["skills"]:
        technical_skills.add(skill["name"])

    consolidated_data["skills"] = [
        {
            "category": "Technical",
            "skills": list(technical_skills)
        },
        {
            "category": "Non-technical",
            "skills": []
        }
    ]
    
    return consolidated_data

def main():
    # Load GitHub data
    with open('github.json', 'r') as f:
        github_data = json.load(f)
    
    # Load LinkedIn data
    with open('linkedin.json', 'r') as f:
        linkedin_data = json.load(f)
    
    # Generate consolidated data
    consolidated_data = process_json_files(github_data, linkedin_data)
    
    # Write to output JSON file
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
