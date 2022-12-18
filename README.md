# lts_stats
1. Add connection string to environment variables - variable name should be LIGHTHOUSE_MONGO_KEY
2. Install relevant packages from Pipfile
3. run python -m streamlit run spreadsheet/webapp.py in the terminal (will use port 8501)

# using docker for dev
1. create .env file in root directory, add LIGHTHOUSE_MONGO_KEY=<your connection string>
2. docker build -t lts_stats .
3. docker run -p 8501:8501 --env-file .env lts_stats