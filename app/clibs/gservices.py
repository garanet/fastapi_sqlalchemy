from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
def google_fetch(item_id):
    try:
# Try the Google API connection and get values from the sheet        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        credentials = Credentials.from_service_account_file('./config/credentials.json', scopes=SCOPES) # TO DO (ENCRYPT OR LOAD IT IN ANOTHER WAY)
        service = build('sheets', 'v4', credentials=credentials)
        SPREADSHEET_ID = item_id
        CELL_RANGE = 'A:C'
    except Exception as error:
        return {"error": {"error_details": str(error)}}
# Sanitize result values to JSON format
    try:            
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=CELL_RANGE).execute()
        values = result.get('values', [])        
        cells = [dict(zip(values[0], row)) for row in values[1:]]
# Add incremental ID and sanitize empty values key.
        new_items = []
        x = 0
        for row in cells :
            x +=1
            row['name'] = item_id  
            row['id'] = x
            row.setdefault('title', '-')
            row.setdefault('image', '-')
            row.setdefault('description', '-')
            new_items.append(row)  
    except Exception as error:
        return {"error": error}
    return new_items