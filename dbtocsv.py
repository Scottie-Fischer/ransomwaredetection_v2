import sqlite3
import pandas as pd

# Open the file
f = open('out.csv', 'w')
# Create a connection and get a cursor
connection = sqlite3.connect('maliciousness.db')
cursor = connection.cursor()
# Execute the query
cursor.execute('select * from ENCRYPTION')
# Get Header Names (without tuples)
colnames = [desc[0] for desc in cursor.description]
# Get data in batches
while True:
    # Read the data
    df = pd.DataFrame(cursor.fetchall())
    # We are done if there are no data
    if len(df) == 0:
        break
    # Let us write to the file
    else:
        df.to_csv(f, header=colnames)

cursor.execute('select * from PREDICTIONS')
# Get Header Names (without tuples)
colnames = [desc[0] for desc in cursor.description]
# Get data in batches
while True:
    # Read the data
    df = pd.DataFrame(cursor.fetchall())
    # We are done if there are no data
    if len(df) == 0:
        break
    # Let us write to the file
    else:
        df.to_csv(f, header=colnames)

# Clean up
f.close()
cursor.close()
connection.close()