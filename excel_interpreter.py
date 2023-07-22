import streamlit as st
import pandas as pd
import json
import openpyxl
import os
import base64
import globalvars
from globalvars import excel_input_test
from gpt_anlyze import create_reflection
from text_anonymization import anonymize_text, de_anonymize_text

global body_content_list
body_content_list = []

def app():
    st.title("Excel Processor")

    global response_json_list
    global body_content_list
    response_json_list = []
    body_content_list = []
    global original_body_list
    original_body_list = []  # New List to store Original Body

    file = st.file_uploader("Upload your Excel file", type=['xlsx', 'xls'])

    def update_excel_input_test(value):
        globalvars.excel_input_test = value

    if file is not None:
        body_content_list.clear()
        original_body_list.clear()  # Clearing List at start of file upload

        try:
            df = pd.read_excel(file)
            df = df.replace('_x000D_', ' ', regex=True)
            st.dataframe(df)

            if 'Body' in df.columns:
                for index, body_first_record in enumerate(df['Body']):
                    original_body_list.append(body_first_record)  # Appending Body to the Original Body List
                    anonymized_text = anonymize_text(body_first_record)
                    update_excel_input_test(anonymized_text)
                    body_content_list.append(anonymized_text)

                    try:
                        response = create_reflection()
                        response_json = response
                        response_json_list.append(response_json)

                        with st.expander("That was sent to GPT", expanded=False):
                            st.write(globalvars.excel_input_test)

                        with st.expander("De-anonymized output from GPT", expanded=False):
                            de_anonymized_response = de_anonymize_text(response_json)
                            st.write(de_anonymized_response)
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
    global original_body_list  # Declaring Original Body List as global

    if not response_json_list:
        st.write("No GPT response to create excel from.")
        return

    st.subheader("Final file")

    df_list = []
    excel_file_name = "Interview_Scheduling_mapping.xlsx"

    for index, json_data in enumerate(response_json_list):
        for key, value in json_data.items():
            if isinstance(value, list):
                json_data[key] = ', '.join(value)

        df = pd.DataFrame(json_data, index=[0])
        df['Anonimized Body'] = body_content_list[index]
        df['Original Body'] = original_body_list[index]  # Adding 'Original Body' column to dataframe

        if isinstance(df['Candidate name'][0], str):
            df['Candidate name'] = df['Candidate name'].apply(lambda x: x.split(', '))

        df = df.explode('Candidate name')
        df = df.explode('Anonimized Body')
        df = df.explode('Original Body')  # Exploding 'Original Body' column

        df_list.append(df)
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
