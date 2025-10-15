import streamlit as st
import pandas as pd
from whatstk import df_from_txt_whatsapp
from collections import defaultdict
from custom_functions import extract_name,convert_df


# Chats Upload

chat_text = st.file_uploader("Choose a WhatsApp group chat file", type=["txt"])

try:
    # Read the content of the uploaded file
    with open(chat_text.name, "wb") as f:
        f.write(chat_text.getbuffer())
    df = df_from_txt_whatsapp(chat_text.name)

except Exception as e:
    st.markdown("Steps to get group chat text file:")
    st.markdown("1) Export group chat from your phone. [Tutorial link](https://youtu.be/1hvw59_0rvQ?si=TTXjlPGBuPzKyRQL)")
    st.markdown("2) Extract and upload the chat text file.")

Category = st.selectbox(
     'Type of Whatsapp group?',
     ('Friend', 'Family', 'Work'))

#dictionary initialization
birthday_dict = defaultdict(set)

if chat_text is not None:
    #Chat data preprocessing
    try:
        df['Date'] = df['date'].dt.date
        birthday_rows = df[df['message'].str.contains('Happy Birthday', na=False)]
        for index, row in birthday_rows.iterrows():
            name = extract_name(row['message'])
            if name is not None:
                birthday_dict[name].add(row['Date'])
    except Exception as e:
        st.markdown(":red[Invalid chat file.]")


if chat_text is not None:
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
        st.markdown(":red[Note - The birth year listed in this table is not accurate.]")

    except Exception as e:
        st.markdown(":red[Failed to generate output.]")
