import numpy as np
import random
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from nltk_utils import bag_of_words, tokenize, stem
from model import RNNModel
import argparse
import os

# Parse command line arguments
parser = argparse.ArgumentParser(description='Train RNN model for symptom checker')
parser.add_argument('--language', type=str, default='en', help='Language code (e.g., en, ta, ml, hi, te)')
parser.add_argument('--intents', type=str, help='Path to intents JSON file')
parser.add_argument('--output', type=str, help='Output path for trained model')

args = parser.parse_args()

current_dir = os.path.dirname(os.path.abspath(__file__))

# Determine intents file and output file
if args.intents:
    intents_path = args.intents
else:
    intents_path = os.path.join(current_dir, f'intents_{args.language}.json')

if args.output:
    output_file = args.output
else:
    output_file = os.path.join(current_dir, f'data_rnn_{args.language}.pth')

with open(intents_path, 'r', encoding='utf-8') as f:
    intents = json.load(f)
    
all_words = []
tags = []
xy = []
# Loop through each sentence in intents patterns
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

ignore_words = ['?', '.', '!', ',']
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

X_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    label = tags.index(tag)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

# Define the RNN model configuration
input_size = len(X_train[0])
hidden_size = 8
output_size = len(tags)
num_layers = 1  # Specify the number of layers for your RNN model

# Create a dataset and data loader for training
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=1, shuffle=True, num_workers=0)

# Set device for training
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize the RNN model
model = RNNModel(input_size, hidden_size, output_size, num_layers).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Train the RNN model
num_epochs = 1000
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)

        words = words.view(-1, len(words), input_size)
        outputs = model(words)
        loss = criterion(outputs, labels)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    if (epoch+1) % 100 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

print(f'Final loss: {loss.item():.4f}')

# Save the trained RNN model
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "num_layers": num_layers,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}

torch.save(data, output_file)

print(f'Training complete. RNN model saved to {output_file}')
