# About
Extracting a list of foods from a sentence.

# Installation
```
    pip install spacy
    python -m spacy download en_core_web_md  
    python -m spacy download en_core_web_md  
```

# Steps
- Create a list of foods that is included in the sample chatbot discussion PDF and save it in a text file named `food-list.txt`.
- Create sentences using the food list and create training data (44 sentences initially) saved as `food_training_data.txt` and validation data (10 sentences) saved as `food_validation_data.txt`.
- We used the [NER Text Annotator tool](https://tecoholic.github.io/ner-annotator/) to annotate the data and identify the `FOOD` (foods) in the training and validation sets.
- Upload the text file (training, then validation).
![Description of the image](images/file_upload.jpg)
- Create a custom tag named 'FOOD' by clicking on the NEW TAG button. 
- Data annotation - highlight all the foods from the datasets.
![Description of the image](images/text_annotation.jpg)
- Export the JSON file resulting from the annotations and save them as `food_training_data.json` and `food_validation_data.json`.
- Run the `food_extractionl.ipynb` file. This will give us a model that has a custom entity label named `FOOD`, which can be used as a guardrail for the user inputs in the Streamlit app.

# Limitations
- The training and validation sets are fairly small.
- The accuracy of the model still needs to be improved.
- Sentiment analysis and negative sentences are not yet handled.
- The model is case-sensitive for now.

# Resources
- [DocBin](https://spacy.io/api/docbin/)
- [tqdm](https://tqdm.github.io/)

