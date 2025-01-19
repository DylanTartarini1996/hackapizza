## Datapizza Hackaton

### Installation

Set up config.env with ENDPOINT (IBM Endpoint), WATSONX_APIKEY and PROJECT_ID environment variable
Create a virtualenv with python3.12 and then run

    pip install -r requirements.txt

### Run submission

    python create_submission_raw.py
    ## Run notebook process_raw_res.ipynb to fix the CSV for release

Set the paths to the question CSV in the script accordingly:

    streamlit run frontend_app.py

