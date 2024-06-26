import streamlit as st
from sec_edgar_downloader import Downloader
import re
import google.generativeai as genai
import os

# Set up Google API key for GenerativeAI
GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Set page configuration for Streamlit app
st.set_page_config(
    page_title="Insight Generator",
    page_icon=":bar_chart:",
)

# Function to load text from a file
def load_text(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print("File not found.")
        return None

# Function to clean HTML tags from text
def cleanhtml(raw_html):
    cleanstring = re.sub(r'<[^>]*>', '', raw_html)
    return re.sub(r'&#.*?;', ' ', cleanstring)

# Function to count words in a string
def string_count(string):
    words = string.split()
    return len(words)
    
# Function to shorten a string
def shorten_text(text):
    len_string = string_count(text) - 20000
    words = text.split()
    shortened_text = ' '.join(words[:-len_string])
    return shortened_text

# Function to extract text between start and end markers
def extract_text(input_string, start_marker, end_marker, prev_end, x):
    input_string = input_string.lower()
    start_marker = start_marker.lower()
    end_marker = end_marker.lower()

    # Find indices of start marker
    start_indices = [i for i in range(len(input_string)) if input_string.startswith(start_marker, i)]
    if (len(start_indices) > 2) :
        if ((start_indices[2]-start_indices[1]) > (start_indices[1]-start_indices[0]+10000)):
            start_index = start_indices[2]
        else:
            start_index = start_indices[1]
    else:
        start_index = start_indices[1]
        
    if start_index == -1:
        return "Start or end marker not found." 

    # Find indices of end marker
    end_indices = [i for i in range(len(input_string)) if input_string.startswith(end_marker, i)]
    if (len(end_indices) > 2) :
        if ((end_indices[2]-end_indices[1]) > (end_indices[1]-end_indices[0]+10000)):
            end_index = end_indices[2]
        else:
            end_index = end_indices[1]
    else:
        end_index = end_indices[1]

    #Make sure that the current start marker is greater than the previous end marker
    j = 1
    while ((j+1< len(start_indices)) and (start_index <= prev_end)):
        start_index = start_indices[j+1]
        j += 1
        
    #Make sure that the end marker is greater than the start marker
    i = 1
    while ((i+1< len(end_indices)) and (end_index <= start_index+1000)):
        end_index = end_indices[i+1]
        i += 1

    if (x==1):
        start_index = start_indices[1] 
        
    if end_index == -1:
        return "Start or end marker not found." 
    return input_string[start_index + len(start_marker):end_index], end_index

# Streamlit UI components
st.title(" :blue[SEC 10K Filing] Insight Generator")
st.divider()
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)
col1, col2= st.columns(2)

# Take ticker and word count as inputs
with col1:
    ticker = st.text_input(
        "Enter the stock ticker 👇",
        placeholder= "GOOGL, MSFT, AAPL, NVDA, etc",
    )

with col2:
    word_count = st.slider('Word Count?', 0, 1000, 100)

# Fetch button to trigger insights generation
if st.button('Fetch'):
    with st.spinner('Fetching Reports and Generating Insights...'):
        # Download the latest SEC 10K filings using sec_edgar_downloader
        dl = Downloader("JJBigDub", "jjbigdub@gmail.com")
        dl.get("10-K", ticker, limit=1)
        parent_folder_path = f"/home/ec2-user/sec10k/sec10k-insight-generator/sec-edgar-filings/{ticker}/10-K"
        directories = [dir for dir in os.listdir(parent_folder_path) if os.path.isdir(os.path.join(parent_folder_path, dir))]
        for directory in directories:
            files = os.listdir(os.path.join(parent_folder_path, directory))
            
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(parent_folder_path, directory, file)
                    with open(file_path, 'r') as f:
                        html_text = f.read()

        cleantext = cleanhtml(html_text)

        st.title(' :green[Business Overview]   :briefcase:')
        st.divider()

        # Generate insights for Business Overview
        Part1_start = "Item 1"
        Part1_end = "Item 1A"
        Part1_text, prev_end = extract_text(cleantext, Part1_start, Part1_end, 0, 1)
        Part1_input = f"Generate insights for the following SEC 10K Filing Part for {ticker} in about {word_count} words. ENSURE THAT YOU FOLLOW THE BELOW 4 GUIDELINES\n 1) Use clear sub-headings with bullet points to discuss key aspects such as Company Overview and Products, Competition, R&D, Sales and Sourcing.\n 2) USE :orange[<insert sub-heading>] for sub-headings.\n 3) Present the answer in a markdown format. 4) Avoid using single or double quotation marks in the response.\n An example of a suitable Format is given as:\n # :orange[Fiscal Year Highlights]\n {ticker}'s fiscal year 2024 witnessed: -\n **Rise in Product & Services Performance:**\n - Successful launch of Products.\n - Growth in Business. \n- Sustained leadership in Technology.\n Format your answer in such a way. The data to be summarised starts below this line. \n {Part1_text}"
        if (string_count(Part1_input) > 20000):
            Part1_input = shorten_text(Part1_input)
        Part1_response = model.generate_content(Part1_input)
        Part1_output = Part1_response.candidates[0].content.parts[0].text
        st.markdown(f"""{Part1_output}""")

        st.title(' :green[Risk Factors]   :exclamation:')
        st.divider()

        # Generate insights for Risk Factors
        Part2_start = "Item 1A"
        Part2_end = "Item 1B"
        Part2_text, prev_end1 = extract_text(cleantext, Part2_start, Part2_end, prev_end, 0)
        Part2_input = f"Generate insights for the following SEC 10K Filing Part for {ticker} in about {word_count} words. ENSURE THAT YOU FOLLOW THE BELOW 4 GUIDELINES\n 1) Use clear sub-headings with bullet points to discuss key aspects such as Macroeconomic and Industry Risks, Business Risks, Legal and Regulatory Compliance Risks, Financial Risks and General Risks. Also discuss some possible ways to mitigate the risks involved.\n 2) USE :orange[<insert sub-heading>] for sub-headings.\n 3) Present the answer in a markdown format.\n 4) Avoid using single or double quotation marks in the response.\n An example of a suitable format is given as:\n # :orange[Fiscal Year Highlights]\n {ticker}'s fiscal year 2024 witnessed: -\n **Rise in Product & Services Performance:**\n - Successful launch of Products.\n - Growth in Business. \n- Sustained leadership in Technology.\n Format your answer in such a way. The data to be summarised starts below this line \n {Part2_text}"
        if (string_count(Part2_input) > 20000):
            Part2_input = shorten_text(Part2_input)
        Part2_response = model.generate_content(Part2_input)
        Part2_output = Part2_response.candidates[0].content.parts[0].text
        st.markdown(f"""{Part2_output}""")

        st.title(' :green[Financial Highlights]   :chart_with_upwards_trend:')
        st.divider()

        # Generate insights for Financial Highlights
        Part3_start = "Item 7"
        Part3_end = "Item 7A"
        Part3_text, _ = extract_text(cleantext, Part3_start, Part3_end, prev_end1, 0)
        Part3_input = f"Generate insights for the following SEC 10K Filing Part for {ticker} in about {word_count} words. ENSURE THAT YOU FOLLOW THE BELOW 4 GUIDELINES\n 1) Use clear sub-headings with bullet points to discuss key aspects such as Fiscal Year Highlights, Products and Services Performance, Segment wise Performance, Operating Expenses and Gross margin, Liquidity and Capital Resources and Conclusion.\n 2) USE :orange[<insert sub-heading>] for sub-headings.\n 3) Present the answer in a markdown format.\n 4) Avoid using single or double quotation marks in the response.\n An example of a suitable format is given as:\n # :orange[Fiscal Year Highlights]\n {ticker}'s fiscal year 2024 witnessed: -\n **Rise in Product & Services Performance:**\n - Successful launch of Products.\n - Growth in Business. \n- Sustained leadership in Technology.\n Format your answer in such a way. The data to be summarised starts below this line \n {Part3_text}"
        if (string_count(Part3_input) > 20000):
            Part3_input = shorten_text(Part3_input)
        Part3_response = model.generate_content(Part3_input)
        Part3_output = Part3_response.candidates[0].content.parts[0].text
        st.markdown(f"""{Part3_output}""")
    st.success('Generation Complete!')
        
