# from flask import Flask, request, jsonify
# from flask_cors import CORS # type: ignore
# import os
# from langchain.chains import create_sql_query_chain
# from langchain_google_genai import GoogleGenerativeAI
# from sqlalchemy import create_engine, text
# from sqlalchemy.exc import ProgrammingError
# from langchain_community.utilities import SQLDatabase # type: ignore
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# # Database connection parameters for PostgreSQL
# db_user = "postgres"
# db_password = "pwd"
# db_host = "localhost"
# db_name = "linkedindb"
# db_port="5432"

# engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}")
# db = SQLDatabase(engine, sample_rows_in_table_info=100)

# # Initialize GoogleGenerativeAI
# llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])

# # Create SQL query chain
# chain = create_sql_query_chain(llm, db)

# def execute_query(question):
#     try:
#         response = chain.invoke({"question": question})

#         # Clean the generated SQL query
#         cleaned_query = response.replace('```sql', '').replace('```', '').strip()
#         if "LIMIT" in cleaned_query.upper():
#             cleaned_query = cleaned_query.rsplit("LIMIT", 1)[0].strip()  # Removes LIMIT clause
        
#         # Execute the cleaned query
#         with engine.connect() as connection:
#             result = connection.execute(text(cleaned_query)).fetchall()

#         return cleaned_query, result
#     except ProgrammingError as e:
#         return None, f"Error: {e}"

# @app.route('/chatbot', methods=['POST'])
# def chatbot():
#     data = request.get_json()
#     question = data.get('question')
    
#     if question:
#         cleaned_query, result = execute_query(question)
#         if cleaned_query:
#             return jsonify({
#                 "query": cleaned_query,
#                 "result": [dict(row) for row in result]  # Convert query result to JSON-serializable format
#             })
#         else:
#             return jsonify({"error": "An error occurred during query execution."}), 500
#     else:
#         return jsonify({"error": "No question provided."}), 400

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()

# Database connection parameters for PostgreSQL
db_user = "postgres"
db_password = "pwd"
db_host = "localhost"
db_name = "alumni"
db_port = "5432"

engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
db = SQLDatabase(engine, sample_rows_in_table_info=100)
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])
chain = create_sql_query_chain(llm, db)

@app.route('/execute', methods=['POST'])
def execute_query():
    data = request.json
    question = data.get('question', '')
    try:
        response = chain.invoke({"question": question})
        cleaned_query = response.replace('```sql', '').replace('```', '').strip()
        if "LIMIT" in cleaned_query.upper():
            cleaned_query = cleaned_query.rsplit("LIMIT", 1)[0].strip()
        with engine.connect() as connection:
            result = connection.execute(text(cleaned_query)).fetchall()
        return jsonify({
            'sqlQuery': cleaned_query,
            'result': [dict(row) for row in result]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
