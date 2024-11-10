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

sample_texts = [
    "Suraj Balaso Malvadkar Phone: +91-9730443473",
    "B.E (Computer Engineering) E-mail: malavadkar.suraj@gmail.com",
    "Willing to work as a key player in challenging & creative field of Information Technology, with leading organization of hi-tech environment having committed & dedicated people, which will help me to explore myself fully and to realize my potential.",
    "Diploma in .NET from MindScripts Pune, 2017, Grade B",
    "B.E(Computer Engineering) from Pune University, 2016, 62.26%, First",
    "Technical Skill: C++, C#.NET, ASP.NET, ADO.NET, Java Scripts",
    "Project: Personal Organization Website using HTML, CSS, JavaScript",
    "Personal Details: Name: Mr.Suraj Balaso Malvadkar, D.O.B: 01, January, 1994",
    "Languages: English, Hindi, Marathi",
    "Hobby: Playing Cricket"
]

# Generate resume data using the fine-tuned BERT model
generated_resume_data = generate_resume_data(sample_texts)
print(generated_resume_data)

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
    model="llama-3.1-8b-instant",
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
generate points only for each section.
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
# Generate each section of the resume
experience_section = generate_resume_section(
    resume_data["experience"]["header"],
    resume_data["experience"]["content"],
    resume_data["experience"]["meta"]
)

education_section = generate_resume_section(
    resume_data["education"]["header"],
    resume_data["education"]["content"],
    resume_data["education"]["meta"]
)

knowledge_section = generate_resume_section(
    resume_data["knowledge"]["header"],
    resume_data["knowledge"]["content"],
    resume_data["knowledge"]["meta"]
)

project_section = generate_resume_section(
    resume_data["project"]["header"],
    resume_data["project"]["content"],
    resume_data["project"]["meta"]
)

others_section = generate_resume_section(
    resume_data["others"]["header"],
    resume_data["others"]["content"],
    resume_data["others"]["meta"]
)

# Combine all sections into the final resume
final_resume = {
    "experience": experience_section,
    "education": education_section,
    "knowledge": knowledge_section,
    "project": project_section,
    "others": others_section
}

# Save the generated resume as a JSON file
with open('final_resume.json', 'w') as f:
    json.dump(final_resume, f, indent=4)

# Combine all sections into the final resume
final_resume = f"""
{experience_section}

{education_section}

{knowledge_section}

{project_section}

{others_section}
"""

# Print the generated resume
print(final_resume)