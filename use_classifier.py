import os
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.preprocessing import LabelEncoder

# Set the device to GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

# Load the test data
def load_test_data(data_dir):
    data = []
    folder_path = os.path.join(data_dir, 'test')
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) == 3:
                    data.append((parts[2],parts[0],parts[1]))  # (text, label)
    return pd.DataFrame(data, columns=['text','class','label'])

data_dir = 'resume_data'
test_df = load_test_data(data_dir)

# Encode the labels
le = LabelEncoder()
test_df['label'] = le.fit_transform(test_df['class'] + test_df['label'])

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModelForSequenceClassification.from_pretrained('./results/checkpoint-6003').to(device)

# Tokenize the test data
test_encodings = tokenizer(test_df['text'].tolist(), truncation=True, padding=True, return_tensors='pt')

# Create a dataset class for the test data
class TestDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

test_labels = test_df['label'].tolist()
test_dataset = TestDataset(test_encodings, test_labels)

# Create a DataLoader for the test data
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=8, shuffle=False)

# Perform inference
model.eval()
predictions = []
with torch.no_grad():
    for batch in test_loader:
        inputs = {key: val.to(device) for key, val in batch.items() if key != 'labels'}
        outputs = model(**inputs)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=-1)
        predictions.extend(preds.cpu().numpy())

# Print the predictions
for text, pred in zip(test_df['text'], predictions):
    print(f'Text: {text}\nPrediction: {le.inverse_transform([pred])[0]}\n')