# Multilingual Symptom Checker Support

This symptom checker now supports multiple languages: English, Tamil, Malayalam, Hindi, and Telugu.

## Current Implementation

### Languages Supported
- **English (en)**: Fully implemented with trained model
- **Tamil (ta)**: Intents created, model needs training
- **Malayalam (ml)**: Intents created, model needs training
- **Hindi (hi)**: Intents created, model needs training
- **Telugu (te)**: Intents created, model needs training

### Files Structure
- `intents_{lang}.json`: Intent patterns and responses for each language
- `data_rnn_{lang}.pth`: Trained PyTorch model for each language (only English available)

### How It Works
1. **Language Detection**: Uses `langdetect` library to detect input language
2. **Model Selection**: Loads appropriate model and intents based on detected language
3. **Response Generation**: Processes input using language-specific model

## Training Models for Other Languages

To train models for Tamil, Malayalam, Hindi, and Telugu:

1. **Prepare Training Data**: Create training data in each language following the same format as English intents
2. **Train Model**: Use the existing training script with language-specific data
3. **Save Model**: Save as `data_rnn_{lang}.pth`

### Example Training Command
```bash
python train_model.py --language ta --intents intents_ta.json --output data_rnn_ta.pth
```

## Adding New Languages

1. Add language code to `languages` list in `chat.py`
2. Create `intents_{lang}.json` with translated intents
3. Train and save model as `data_rnn_{lang}.pth`

## Dependencies
- `langdetect==1.0.9`: For language detection
- PyTorch: For model inference
- NLTK: For tokenization

## Notes
- Fallback to English if language detection fails
- Basic tokenization used for non-English languages
- Models need to be trained separately for each language
