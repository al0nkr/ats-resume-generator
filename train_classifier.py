import os
import pandas as pd
from sklearn.model_selection import train_test_split
import torch
from transformers import AutoTokenizer
from sklearn.preprocessing import LabelEncoder

from transformers import AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments

# Set the device to GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

def load_data(data_dir):
    data = []
    for folder in ['train', 'test', 'valid']:
        folder_path = os.path.join(data_dir, folder)
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split('\t')
                    if len(parts) == 3:
                        data.append((parts[2], parts[0] ,parts[1]))  # (text, class ,label)
    return pd.DataFrame(data, columns=['text','class','label'])

data_dir = 'resume_data'
df = load_data(data_dir)

le = LabelEncoder()
df['label'] = le.fit_transform(df['class'] + df['label'])

# Split the data into training and validation sets
train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)

train_df = train_df.to_dict('records')
val_df = val_df.to_dict('records')

train_encodings = tokenizer([x['text'] for x in train_df], truncation=True, padding=True)
val_encodings = tokenizer([x['text'] for x in val_df], truncation=True, padding=True)

class ResumeDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_labels = [x['label'] for x in train_df]
val_labels = [x['label'] for x in val_df]

train_dataset = ResumeDataset(train_encodings, train_labels)
val_dataset = ResumeDataset(val_encodings, val_labels)

model = AutoModelForSequenceClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=len(set(df['label']))
).to(device)  # Move model to GPU

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    fp16=True,  # Enable mixed precision training for faster performance
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()