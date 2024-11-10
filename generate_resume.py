import os
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import json
# Input data for the resume

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "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"


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

# Define unique classes and labels
unique_classes = ["header", "content", "meta"]
unique_labels = ["experience", "education", "knowledge", "project", "others"]

# Encode the labels
le = LabelEncoder()
le.fit([f"{cls}_{lbl}" for cls in unique_classes for lbl in unique_labels])

tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModelForSequenceClassification.from_pretrained('./results/checkpoint-6003').to(device)  # change to model path

# Use the fine-tuned BERT model to generate resume data
def generate_resume_data(texts):
    model.eval()
    resume_data = []
    with torch.no_grad():
        for text in texts:
            inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(device)
            outputs = model(**inputs)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=-1).cpu().numpy()[0]
            resume_data.append((text, le.inverse_transform([pred])[0]))
    return resume_data

with open('test.json', 'r', encoding='utf-8') as f:
    sample_texts = [str(value) for value in json.load(f).values()]
    sample_texts = []

def extract_values(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            extract_values(value)
    elif isinstance(obj, list):
        for item in obj:
            extract_values(item)
    else:
        sample_texts.append(str(obj))

with open('test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    extract_values(data)


# Generate resume data using the fine-tuned BERT model
generated_resume_data = generate_resume_data(sample_texts)

# Map the generated resume data to the required format
resume_data = {
    "experience": {
        "header": "Experience",
        "content": generated_resume_data[0][0],
        "meta": generated_resume_data[0][1]
    },
    "education": {
        "header": "Education",
        "content": generated_resume_data[1][0],
        "meta": generated_resume_data[1][1]
    },
    "knowledge": {
        "header": "Knowledge",
        "content": generated_resume_data[2][0],
        "meta": generated_resume_data[2][1]
    },
    "project": {
        "header": "Projects",
        "content": generated_resume_data[3][0],
        "meta": generated_resume_data[3][1]
    },
    "others": {
        "header": "Others",
        "content": generated_resume_data[4][0],
        "meta": generated_resume_data[4][1]
    }
}
# Initialize the language model
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)
# Create a prompt template for each section
section_template = """
Using the provided resume data, generate a professional resume section which includes metrics and is ATS Friendly.

{header}
Content: {content}
Meta: {meta}

Ensure the section is well-formatted and no line should exceed 40 words.
Also ensure only content is generated and no additional text is added.
"""

section_prompt = PromptTemplate(
    input_variables=["header", "content", "meta"],
    template=section_template
)

# Assign prompt chains to LangChain
section_chain = LLMChain(llm=llm, prompt=section_prompt)

# Function to generate each section of the resume
def generate_resume_section(header, content, meta):
    inputs = {
        "header": header,
        "content": content,
        "meta": meta
    }
    return section_chain.run(inputs)

with open('test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    name = data.get('name', '')
    contact = data.get('contact', {})
    summary = data.get('summary', '')

# Prepare the prompt for groq chat with name, contact, and summary
personal_info_template = """
Using the provided personal information, generate a professional resume introduction that is ATS Friendly.

Name: {name}
Contact:
  Email: {email}
  Phone: {phone}
Summary: {summary}

Generate a professional introduction that includes the name, contact information.
Ensure the introduction is well-formatted and no line should exceed 40 words. and no additional text is added, only formatted resume content
"""

personal_info_prompt = PromptTemplate(
    input_variables=["name", "email", "phone", "summary"],
    template=personal_info_template
)

# Create a chain for personal information
personal_info_chain = LLMChain(llm=llm, prompt=personal_info_prompt)

# Generate the personal information section
personal_info_section = personal_info_chain.run({
    "name": name,
    "email": contact.get('email', ''),
    "phone": contact.get('phone', ''),
    "summary": summary
})

# Now, extract education, projects, and experiences to pass to generate_resume_data
sample_texts = []

def extract_texts(section_data, key_name):
    extracted_texts = []
    if isinstance(section_data, list):
        for item in section_data:
            if isinstance(item, dict):
                extracted_texts.append(item)
    return extracted_texts

education_texts = extract_texts(data.get('education', []), 'education')
project_texts = extract_texts(data.get('projects', []), 'projects')
experience_texts = extract_texts(data.get('experiences', []), 'experiences')

# Combine all texts for generate_resume_data
sample_texts.extend(education_texts)
sample_texts.extend(project_texts)
sample_texts.extend(experience_texts)

# Generate resume data using the fine-tuned BERT model
generated_resume_data = generate_resume_data([json.dumps(text) for text in sample_texts])

# Map the generated resume data to the required format
resume_data = {}
for idx, (content, label) in enumerate(generated_resume_data):
    section_key = f"section_{idx}"
    resume_data[section_key] = {
        "header": label.capitalize(),
        "content": content,
        "meta": label
    }

print(resume_data)
# Generate each section of the resume
sections = {}
for key, value in resume_data.items():
    section_text = generate_resume_section(
        value["header"],
        value["content"],
        value["meta"]
    )
    sections[key] = section_text

# Combine all sections into the final resume
final_resume = personal_info_section + "\n\n"
for section in sections.values():
    final_resume += section + "\n\n"

# Save the generated resume as a JSON file
with open('final_resume.json', 'w') as f:
    json.dump({"resume": final_resume}, f, indent=4)

# Print the generated resume
print(final_resume)