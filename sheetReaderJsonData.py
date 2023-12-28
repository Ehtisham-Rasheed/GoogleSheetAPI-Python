import requests
import json
import pdb
from flask import Flask, request, jsonify
import gspread
from datetime import datetime, date, time
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2 import service_account

app = Flask(__name__)

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file('creds.json',scopes=scopes)

client = gspread.authorize(credentials)

source_sheet = client.open('UnderlyingDataForTheLosses from the exchange rate gap visualization - Team')

# selecting the sheet and getting all the recoreds from sheet
source_sheet = source_sheet.get_worksheet(1)
source_data = source_sheet.get_all_values()

# zipping the header with each row and converting the result into dictionary 
header = source_data[0]
data_objects = [dict(zip(header, row)) for row in source_data[1:]]

# decorator/API is starting from here
@app.route('/api/transfer_date_range_data/', methods=['GET'])
def transfer_range_data():
 
#  getting the start and end date that user passes from the browser
 first_date = request.args.get("first-date")
 second_date = request.args.get("second-date")
 
#  converting the date into date object
 first_date = datetime.strptime(first_date, "%Y-%m-%dT%H:%M:%SZ")
 second_date = datetime.strptime(second_date, "%Y-%m-%dT%H:%M:%SZ")

#  filtering the records or data based on the given date range
 filtered_data = [x for x in data_objects if 
                  (first_date <= datetime.strptime(x["Time"], "%Y-%m-%dT%H:%M:%SZ") 
                   and second_date >= datetime.strptime(x["Time"], "%Y-%m-%dT%H:%M:%SZ"))]

#  Selecting only first two keys and changing their names
 selected_data = []
 for x in filtered_data:
    selected_data.append({"timestamp":x["Time"], "loss":x["United Nation rate"]})

 return jsonify(selected_data)

if __name__ == '__main__':
    app.run(debug=True)