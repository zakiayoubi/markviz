## Read this before you use this package. 
To run the app: 
type in the console from the project root: uvicorn app.main:app --reload (for reload on changes)

To run the test:
type in the console from the project root: pytest -vvs

## Run the app with Docker (easiest & recommended)

### 1. Pull the latest image
```bash
docker pull zakiayoubi/markviz:latest

# 1. Build the image locally (uses your Dockerfile)
docker build -t markviz:latest .

# run this command: 

docker run -p 8000:8000 -e FMP_API_KEY=YOUR_OWN_API_KEY zakiayoubi/markviz:latest

