import streamlit as st
from openai import OpenAI
import json
import requests
import os

# Configuration Variables
API_KEY = os.environ.get('OPENAI_API_KEY')
LOGIC_APP_URL = "https://prod-61.eastus.logic.azure.com:443/workflows/8a66494181d947ddb3da2af32ac0f572/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=sssTXiPmAlnvHMPVp240-RypDcFgUY6ozYZ0LjmeVmA"

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)

def call_openai(transcript):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
             messages=[
            {"role": "system", "content": """You are an AI assistant that helps automatically structure quality complaints for Medtronic in a schema format.
 
You should collect the following information from the transcript: Caller Name, Callback Number, Product, Patient Name (if given), Date, Time, Location, Product Make/Model, Serial or Lot number, Description of complaint
 
Return in JSON format;
 
{  
  "Caller Name": "XXX",  
  "Callback Number": "XXX",  
  "Product": "XXX",  
  "Patient Name": "XXX",  
  "Patient ID": "XXX",  
  "Date": "XXX",  
  "Time": "XXX",  
  "Location": "XXX",  
  "Product Make/Model": "XXX",  
  "Serial or Lot number": "XXX",  
  "Description of complaint": "XXX"  
}  
 
If it's not provided, write "N/A"""},
            {"role": "user", "content": transcript},
        ]
        
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in calling OpenAI: {e}")
        return None

st.title('Medtronic Complaints Assistant')
transcript = st.text_area('Enter your transcript:', '')

if 'output' not in st.session_state:
    st.session_state.output = {}

if st.button('Submit'):
    output = call_openai(transcript)
    if output:
        st.session_state.output = json.loads(output)

if st.session_state.output:
    for key in st.session_state.output.keys():
        st.session_state.output[key] = st.text_input(f'{key}:', st.session_state.output[key])

if st.button('Save', key='save'):
    with st.spinner('Saving...'):
        try:
            with open('output.json', 'w') as f:
                json.dump(st.session_state.output, f)
            # Logic to send JSON
            headers = {'Content-Type': 'application/json'}
            response = requests.post(LOGIC_APP_URL, headers=headers, data=json.dumps(st.session_state.output))
            if response.status_code == 200:
                st.balloons()
                st.success('Saved Successfully!')
            else:
                st.error('Failed to save. Please check the log.')
        except Exception as e:
            st.error(f"Failed to save: {e}")
