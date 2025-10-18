import random
import json
import torch
import langdetect

import math
import geocoder
import sys
import os

# Add current directory to path for absolute imports
sys.path.append(os.path.dirname(__file__))

from model_chat import RNNModel  # Import the RNN model
from nltk_utils import bag_of_words, tokenize
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load models and intents for each language
languages = ['en', 'ta', 'ml', 'hi', 'te']  # English, Tamil, Malayalam, Hindi, Telugu

models = {}
intents_data = {}
all_words_data = {}
tags_data = {}

for lang in languages:
    intents_path = os.path.join(current_dir, f'intents_{lang}.json')
    with open(intents_path, 'r', encoding='utf-8') as json_data:
        intents_data[lang] = json.load(json_data)

    model_path = os.path.join(current_dir, f'data_rnn_{lang}.pth')
    if os.path.exists(model_path):
        data = torch.load(model_path)

        input_size = data["input_size"]
        hidden_size = data["hidden_size"]
        output_size = data["output_size"]
        num_layers = data["num_layers"]
        all_words_data[lang] = data['all_words']
        tags_data[lang] = data['tags']
        model_state = data["model_state"]

        model_lang = RNNModel(input_size, hidden_size, output_size, num_layers).to(device)
        model_lang.load_state_dict(model_state)
        model_lang.eval()
        models[lang] = model_lang
    else:
        # For languages without trained models, use English as fallback
        # Load intents but skip model loading, use English data
        all_words_data[lang] = all_words_data['en']
        tags_data[lang] = tags_data['en']

bot_name = "Sam"

# Global variable for manual language override
current_lang = None

def get_response(msg):
    global current_lang
    if current_lang is not None:
        lang = current_lang
    else:
        try:
            lang = langdetect.detect(msg)
        except:
            lang = 'en'
        if lang not in models:
            lang = 'en'

    # Check for language change command
    if msg.startswith("/lang "):
        parts = msg.split()
        if len(parts) > 1:
            new_lang = parts[1].lower()
            if new_lang == "auto":
                current_lang = None
                return ["lang_change", "Language detection set to automatic.", "", ""]
            elif new_lang in languages:
                current_lang = new_lang
                return ["lang_change", f"Language changed to {new_lang.upper()}.", "", ""]
            else:
                return ["lang_change", f"Unsupported language: {new_lang}. Supported: en, ta, ml, hi, te, auto.", "", ""]

    sentence = tokenize(msg)
    if lang != 'en':
        # For non-English, tokenization might need to be adapted or use original msg split
        sentence = msg.split()

    if ("name" in sentence) or ("this is" in msg.lower()) :
        for wor in sentence:
            if (wor.lower() != "my") and (wor.lower() != "is") and (wor.lower() != "name") and (wor.lower() != "i") and (wor.lower() != "am") and (wor.lower() != "this"):
                user_name = wor.capitalize()
                res = "Hi " + user_name + " please say your age."
                return ["name", res, "", ""]
    if ("age" in sentence) or ("I" in sentence and "am" in sentence) or ("I'm" in sentence):
        for wor in sentence:
            if wor.isnumeric():
                user_age = wor
                res = "What is your gender?"
                return ["age", res, "", ""]
    if ("male" in sentence) or ("female" in sentence) or ("Male" in sentence) or ("Female" in sentence):
        for wor in sentence:
            if (wor.lower() == "male") or (wor.lower() == "female"):
                user_gender = wor.lower()
                res = "Tell the symptoms you have to know about potential conditions."
                return ["gender", res, "", ""]
    if ("yes" in sentence) or (("medical" in sentence) and "center" in sentence) or ("hospital" in sentence) or ("hospitals" in sentence) :
        li = centres()
        # centres() returns list starting with "center" tag and then center info
        # Ensure it has 4 elements for frontend
        if len(li) < 4:
            li.extend([""] * (4 - len(li)))
        return li[:4]

    all_words = all_words_data[lang]
    model = models[lang]
    tags = tags_data[lang]
    intents = intents_data[lang]

    X = bag_of_words(sentence, all_words)
    X = torch.tensor(X).unsqueeze(0).unsqueeze(0).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][int(predicted.item())]

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if intent["tag"] == tag:
                if tag in ["greeting", "goodbye","work","who","Thanks","joke", "name", "age", "gender"]:
                    # Return 4 elements, fill missing with empty strings
                    return [intent['tag'], intent['responses'], "", ""]
                # For other tags, return tag, responses, Precaution, and empty string if no extra
                precaution = intent.get('Precaution', "")
                return [intent['tag'], intent['responses'], precaution, ""]
    return ["not_understand","I do not understand. Can you please rephrase the sentence?", "", ""]

def centres():
    # Function to calculate the Haversine distance between two points
    def haversine(lat1, lon1, lat2, lon2):
        # Radius of the Earth in kilometers
        R = 6371.0

        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Calculate the distance
        distance = R * c
        return distance

    # Get your current location based on your IP address
    location = geocoder.ip('me')

    # Given location (latitude and longitude)
    given_location = location.latlng  # Replace with your desired location

    # Load the JSON data
    medical_centers_path = os.path.join(current_dir, "medical_centers.json")
    with open(medical_centers_path, "r") as json_file:
        medical_centers = json.load(json_file)

    # Calculate distances to all medical centers
    distances_to_centers = []

    for center in medical_centers["intents"]:
        center_location = center["location"]
        distance = haversine(given_location[0], given_location[1], center_location[0], center_location[1])
        distances_to_centers.append((center["tag"], distance))

    # Sort the list of distances in ascending order
    distances_to_centers.sort(key=lambda x: x[1])

    l = ["center"]

    for i, (center_name, distance) in enumerate(distances_to_centers[:5], start=1):
        for center in medical_centers["intents"]:
            if center["tag"] == center_name:
                l.append(center_name)
                l.append(str(round(distance, 2)) + 'km')
                l.append(center["Address"])
    return l


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print("Bot:", resp)
