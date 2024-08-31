import streamlit as st
import re
import pandas as pd
from whatstk import df_from_txt_whatsapp
from collections import defaultdict

def extract_phone_number(message):
    pattern = r'91(\d{10,15})'
    match = re.search(pattern, message)
    if match:
        return match.group(1)
    return None

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode("utf-8")


chat_text = st.file_uploader("Choose a WhatsApp group chat file", type=["txt"])

try:
    # Read the content of the uploaded file
    with open(chat_text.name, "wb") as f:
        f.write(chat_text.getbuffer())
    df = df_from_txt_whatsapp(chat_text.name)

except Exception as e:
    # st.error("An unexpected error occurred.")
    # st.exception(e)
    st.markdown("Steps to get group chat text file:")
    st.markdown("1) Export group chat from your phone. [Tutorial link](https://youtu.be/1hvw59_0rvQ?si=TTXjlPGBuPzKyRQL)")
    st.markdown("2) Extract and upload the chat text file.")

contact_csv = st.file_uploader("Choose a csv file for contacts", type=["csv"])

try:
    with open(contact_csv.name, "wb") as f:
        f.write(contact_csv.getbuffer())
    contacts = pd.read_csv(contact_csv.name)

except Exception as e:
    # st.error("An unexpected error occurred.")
    # st.exception(e)
    st.markdown("Import your contacts from [Google Contacts](https://contacts.google.com/) and upload. [Tutorial link](https://www.youtube.com/watch?v=UE2nthOgKIA)")
    st.markdown(":red[Note - Only contacts csv from google contacts is accepted.]")

Category = st.selectbox(
     'Type of Whatsapp group?',
     ('Friend', 'Family', 'Work'))

#dictionary initialization
contact_dict = defaultdict(list)
birthday_dict = defaultdict(set)

#Contacts preprocessing
if contact_csv is not None:
    try:
        contacts = contacts[['First Name', 'Phone 1 - Value']]
        contacts['Name'] = contacts['First Name'].astype(str)
        contacts['Phone 1 - Value'] = contacts['Phone 1 - Value'].astype(str)
        contacts['Phone 1 - Value'] = contacts['Phone 1 - Value'].apply(lambda x: ''.join(x.split()))
        for index, row in contacts.iterrows():
            phone_number = extract_phone_number(row['Phone 1 - Value'])
            if phone_number is None:
                if len(row['Phone 1 - Value']) == 10:
                    phone_number = row['Phone 1 - Value']
            name = row['Name'].split()[0]
            if len(row['Name'].split()) > 1:
                name = name + ' ' + row['Name'].split()[1]
            if phone_number and name:
                contact_dict[phone_number].append(name)
    except Exception as e:
        st.markdown(":red[Invalid contacts file.]")

if chat_text is not None:
    #Chat data preprocessing
    try:
        df['Date'] = df['date'].dt.date
        birthday_rows = df[df['message'].str.contains('Happy Birthday', na=False)]
        for index, row in birthday_rows.iterrows():
            phone_number = extract_phone_number(row['message'])
            if phone_number and contact_dict[phone_number]:
                birthday_dict[contact_dict[phone_number][0]].add(row['Date'])
    except Exception as e:
        st.markdown(":red[Invalid chat file.]")


if chat_text is not None and contact_csv is not None:
    #Output csv generation
    try:
        birthday_df = pd.DataFrame.from_dict(birthday_dict, orient='index')
        out_df = pd.DataFrame({'Name':birthday_df.index,'Birth date':birthday_df[0]})
        out_df.reset_index(drop=True, inplace=True)
        out_df['Category'] = Category
        out_df.to_csv('out.csv',index=False)
        st.write(out_df)
        out_csv = convert_df(out_df)
        st.download_button(
            label="Download Birthday Data",
            data=out_csv,
            file_name='Birthday_data.csv',
            mime='text/csv'
        )
        st.markdown("You can upload this CSV to [🥳 Notion Template](https://peridot-pamphlet-cb4.notion.site/Birthday-calendar-916245c06332480d9cb72813c9d91156?pvs=4). First make account on Notion then go through [Tutorial link](https://youtu.be/KpMdEcNgbV0).")

    except Exception as e:
        st.markdown("")
