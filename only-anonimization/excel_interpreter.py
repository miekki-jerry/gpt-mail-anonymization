import streamlit as st
import pandas as pd
import json
import openpyxl
import os
import base64
import globalvars
from globalvars import excel_input_test
from gpt_anlyze import create_reflection   # Import the function from gpt_analyze

global body_content_list
body_content_list = []

def app():
    st.title("Excel Processor")

    # Declare response_json_list as global
    global response_json_list
    # Initialize response_json_list as an empty list
    response_json_list = []

    file = st.file_uploader("Upload your Excel file", type=['xlsx', 'xls'])

    def update_excel_input_test(value):
        globalvars.excel_input_test = value

    if file is not None:
        # clear 'Body' content list for a new file
        body_content_list.clear()

        try:
            df = pd.read_excel(file)
            df = df.replace('_x000D_', ' ', regex=True)
            st.dataframe(df)

            # Check if 'Body' column is present
            if 'Body' in df.columns:
                for index, body_first_record in enumerate(df['Body']):  # Process each record in 'Body'
                    update_excel_input_test(body_first_record)
                    # add body content to the list
                    body_content_list.append(body_first_record)
                    
                    # Call the function from 'gpt_analyze.py' and print the response
                    try:
                        response = create_reflection()
                        response_json = json.loads(response)
                        response_json_list.append(response_json)  # Add response to the list

                        # Output from GPT shown in an optional dropdown
                        with st.expander("Show OUTPUT FROM GPT", expanded=False):
                            st.write(response_json)   # Display the response in the Streamlit app
                    except json.JSONDecodeError:
                        st.write("Error! The response from GPT is not a valid JSON.")

            else:
                st.write("No 'Body' column in the provided file.")

        except Exception as e:
            st.write("Oops! An error occurred!")
            st.write(e)

def create_excel_from_json(json_data, file_name):
    for key, value in json_data.items():
        if isinstance(value, list):
            json_data[key] = ', '.join(value)

    df = pd.DataFrame(json_data, index=[0])
    df.to_excel(file_name, index=False)


def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def excel_output():
    global response_json_list
    global body_content_list

    if not response_json_list:
        st.write("No GPT response to create excel from.")
        return

    st.subheader("Final file")

    df_list = []  # list to store dataframes
    excel_file_name = "Interview_Scheduling_mapping.xlsx"

    for index, json_data in enumerate(response_json_list):
        for key, value in json_data.items():
            if isinstance(value, list):
                json_data[key] = ', '.join(value)

        df = pd.DataFrame(json_data, index=[0])
        df['Body'] = body_content_list[index]  # add 'Body' column before exploding

        # Converting 'Candidate name' into list
        if isinstance(df['Candidate name'][0], str):
            df['Candidate name'] = df['Candidate name'].apply(lambda x: x.split(', '))

        # Explode 'Candidate name' and 'Body' columns
        df = df.explode('Candidate name')
        df = df.explode('Body')

        df_list.append(df)  # append the dataframe to the list

    final_df = pd.concat(df_list, ignore_index=True) 

    try:
        final_df.to_excel(excel_file_name, index=False)
    except Exception as e:
        st.write(f"Oops! An error occurred while creating the Excel file: {str(e)}")
        return

    try:
        final_df = pd.read_excel(excel_file_name)
        final_df = final_df.replace('_x000D_', ' ', regex=True)
        st.dataframe(final_df)

        st.markdown(get_table_download_link(final_df, excel_file_name, 'Download excel file'), unsafe_allow_html=True)
        
    except Exception as e:
        st.write(f"Oops! An error occurred while reading the Excel file: {str(e)}")

    finally:
        if os.path.exists(excel_file_name):
            os.remove(excel_file_name)
        else:
            st.write(f"The file {excel_file_name} does not exist")




if __name__ == "__main__":
    app()
    excel_output()