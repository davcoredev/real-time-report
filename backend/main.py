from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pyodbc
import asyncio
import socketio
import uvicorn
import toml

# Load the secrets (server, database, user, password)
secrets = toml.load('secrets.toml')

# FastAPI app
app = FastAPI()

# Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app_asgi = socketio.ASGIApp(sio, app)

# Mount static files
app.mount('/static', StaticFiles(directory='../frontend'), name='static')

# SQL Server connection
def get_db_connection():
    return pyodbc.connect(
        "DRIVER={ODBC DRIVER 17 for SQL Server};SERVER="
        +secrets["server"]
        +";DATABASE="
        +secrets["database"]
        +";UID="
        +secrets["username"]
        +";PWD="
        +secrets["password"]
    )

# Fetch data
async def fetch_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(secrets['query'])
    rows = cursor.fetchall()
    conn.close()
    return [{'equipment':row.CurrentEquipment, 
             'seconds':row.SecondsSinceLastOcurrence,
             'status': 'Running' if row.SecondsSinceLastOcurrence >= 15 else 'Stopped' } for row in rows]

# Background task for real-time updates
async def push_updates():
    while True:
        data = await fetch_data()
        await sio.emit('update', data)
        await asyncio.sleep(60) # update every minute

# Serve the frontend
@app.get('/')
async def serve_frontend():
    return FileResponse('../frontend/index.html')

# Start background task
@app.on_event('startup')
async def startup_event():
    asyncio.create_task(push_updates())
    
if __name__ == '__main__':
    uvicorn.run(app_asgi, host='0.0.0.0', port=8000)