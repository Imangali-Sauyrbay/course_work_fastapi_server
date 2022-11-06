import sys
import uvicorn
from app.http.server.server import main as config_server

server = config_server()

if __name__ == "__main__":
    uvicorn.run('main:server', port=8000, workers=3, reload= ('-r' in sys.argv))
