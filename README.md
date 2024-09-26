# Title
Building a customer onboarding chatbot capable of collecting essential user data, including health concerns, through engaging dialogues.

# About
This project focuses on developing an AI-driven chatbot designed to guide users through meal planning and dietary management services. The application aims to provide an effective and user-friendly experience by recommending personalized meal plans and recipes based on user input.

# Technology
| Technology      | Use Case                                      |
|-----------------|-----------------------------------------------|
| Streamlit       | Python framework for creating interactive web applications  |
| SpaCy           | NLP library used to create a Named Entity Recognition model |
| TextBlob        | Library used to perform sentiment analysis to recognize users' preferences |
| OpenAI API      | Used to generate meal plans based on user inputs               |
| LangChain       | Framework for building applications with large language models (Exploration) |
| LangGraph       | Tool for visualizing and managing conversational flows (Exploration) |

# Methodology
## Data Collection
- Food preferences and special needs data were manually collected from sources such as the US Department of Health, the Mayo Clinic, and the Cleveland Clinic allergy disease webpages.
- Additional food data was collected through web scraping using the Beautiful Soup library. The code is available in the [web-scraping folder](/web-scraping/).

## Data Preparation
- The collected entities were incorporated into sentences. Two different files have been created for training and validation purposes.
- A [NER Text Annotator tool](https://tecoholic.github.io/ner-annotator/) was used to annotate the data and identify different entities such as `FOOD`, `SPECIALNEEDS`, and `PREFERENCES` in the training and validation sets.
- The exported JSON files from the tool will be used as the training and validation data to create the SpaCy NER model. These files, `all_train_data.json` and `all_validation_data.json`, can be found in the [NER folder](/NER/data/).

## Model Creation
- The SpaCy NER model is created by running the [spaCy_model.ipynb file](/NER/spaCy_model.ipynb).
- The JSON training and validation data are converted into SpaCy objects.
- The model is trained on the created SpaCy objects using a generated config file.
- The NER model is saved in the [model-best folder](/NER/model-best/).

## Inference
- The accuracy of the NER model can be tested by loading the `model-best` and testing examples of user inputs. See examples in [test/model-test.ipynb](/test/model-test.ipynb).

## Deployment
The app was deployed using the Streamlit app deployment service. All the code is saved in this GitHub repository, which is linked to the Streamlit community cloud. All the libraries required for the project are defined in the `requirements.txt` file, which is necessary for deployment.