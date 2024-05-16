from dbConnector import dbConnector

db = dbConnector.Instance()
TOKEN=db.select_single("select value from settings where key='token'")
print(TOKEN)