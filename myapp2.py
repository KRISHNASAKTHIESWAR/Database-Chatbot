import os
import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import create_engine,text
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
from textblob import TextBlob


load_dotenv()

# Database connection parameters for PostgreSQL
db_user = "postgres"
db_password = "pwd"
db_host = "localhost"
db_name = "alumni"
db_port="5432"


engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}")

db = SQLDatabase(engine, sample_rows_in_table_info=100)


llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])

# Create SQL query chain
chain = create_sql_query_chain(llm, db)

def correct_spelling(input_text):
    blob = TextBlob(input_text)
    corrected_text = str(blob.correct())
    return corrected_text

def execute_query(question):
    try:
        # Correct spelling errors
        corrected_question = correct_spelling(question)
        st.write(f"Corrected Question: {corrected_question}")
        
        # Generate query
        response = chain.invoke({"question": question})
        print(f"Raw Response: {response}")

        # Clean and adjust query
        cleaned_query = response.replace('```sql', '').replace('```', '').strip()
        print(f"Generated SQL Query: {cleaned_query}")

        if "LIMIT" in cleaned_query.upper():
            cleaned_query = cleaned_query.rsplit("LIMIT", 1)[0].strip()
            print(f"Adjusted SQL Query without LIMIT: {cleaned_query}")

        # Execute query
        with engine.connect() as connection:
            result = connection.execute(text(cleaned_query))
            rows = result.fetchall()
            columns = result.keys()
            
        return cleaned_query, {"columns": columns, "rows": rows}
    except ProgrammingError as e:
        st.error(f"An error occurred: {e.orig}")
        print(f"ProgrammingError Details: {e}")
        return None, None


st.title("Question Answering App")


question = st.text_input("Enter your question:")

if st.button("Execute"):
    if question:
        cleaned_query, query_result = execute_query(question)
        
        if cleaned_query and query_result is not None:
            st.write("Generated SQL Query:")
            st.code(cleaned_query, language="sql")
            st.write("Query Result:")
            st.write(query_result)
        else:
            st.write("No result returned due to an error.")
    else:
        st.write("Please enter a question.")

# import os
# import streamlit as st
# from langchain.chains import create_sql_query_chain
# from langchain_google_genai import GoogleGenerativeAI
# from sqlalchemy import create_engine, text
# from sqlalchemy.exc import ProgrammingError
# from langchain_community.utilities import SQLDatabase
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Database connection parameters for PostgreSQL
# db_user = "postgres"
# db_password = "pwd"
# db_host = "localhost"
# db_name = "linkedindb"
# db_port = "5432"

# # Create SQLAlchemy engine
# engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# # Initialize SQL database wrapper
# db = SQLDatabase(engine, sample_rows_in_table_info=100)

# # Initialize Google Generative AI
# llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])

# # Create SQL query chain
# chain = create_sql_query_chain(llm, db)

# def execute_query(question):
#     try:
#         response = chain.invoke({"question": question})
#         cleaned_query = response.replace('\nsql', '').replace('\n', '').strip()
        
#         if "LIMIT" in cleaned_query.upper():
#             cleaned_query = cleaned_query.rsplit("LIMIT", 1)[0].strip()
        
#         with engine.connect() as connection:
#             result = connection.execute(text(cleaned_query)).fetchall()
                
#         return cleaned_query, result
#     except ProgrammingError as e:
#         st.error(f"An error occurred: {e}")
#         return None, None

# st.title("Question Answering App")

# question = st.text_input("Enter your question:")

# if st.button("Execute"):
#     if question:
#         cleaned_query, query_result = execute_query(question)
        
#         if cleaned_query and query_result is not None:
#             st.write("Generated SQL Query:")
#             st.code(cleaned_query, language="sql")
#             st.write("Query Result:")
#             st.write(query_result)
#         else:
#             st.write("No result returned due to an error.")
#     else:
#         st.write("Please enter a question.")
