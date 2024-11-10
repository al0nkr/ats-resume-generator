import os
import json
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

# Set up ChatGroq similar to generate_resume.py
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# Read the final_resume.json file
with open('final_resume.json', 'r', encoding='utf-8') as f:
    final_resume_data = json.load(f)

final_resume_text = final_resume_data.get('resume', '')

# Read the schema from random.json
with open('random.json', 'r', encoding='utf-8') as f:
    random_schema = json.load(f)

schema_text = json.dumps(random_schema, indent=4)

# Create a prompt to ask the LLM to format the resume into random.json format
prompt_template = """
Given the following resume text:

{resume_text}

Convert this resume into a JSON format matching the schema below:

{schema}

Ensure that the output JSON matches the schema exactly, and all fields are populated appropriately based on the resume text.
only give json output and nothing else without backticks
"""

prompt = PromptTemplate(
    input_variables=["resume_text", "schema"],
    template=prompt_template
)

chain = LLMChain(llm=llm, prompt=prompt)

# Generate the formatted resume
formatted_resume_text = chain.run({
    "resume_text": final_resume_text,
    "schema": schema_text
})
print(formatted_resume_text)

# Parse the output as JSON
try:
    formatted_resume_json = json.loads(formatted_resume_text)
except json.JSONDecodeError:
    print("Error parsing JSON output from LLM.")
    formatted_resume_json = {}

# Save the formatted resume to formatted_resume.json
with open('formatted_resume.json', 'w', encoding='utf-8') as f:
    json.dump(formatted_resume_json, f, indent=4)

# Print the formatted resume
print(json.dumps(formatted_resume_json, indent=4))