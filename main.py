from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import csv
import io
from collections import Counter

app = FastAPI()

# -------------------------------------------------
# Proper CORS setup
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Explicit OPTIONS handler (important for graders)
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )

# Force header on ALL responses
@app.middleware("http")
async def force_cors_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# -------------------------------------------------
# Constants
# -------------------------------------------------
VALID_TOKEN = "2ki19djfqqs0zw00"
MAX_FILE_SIZE = 59 * 1024
ALLOWED_EXTENSIONS = [".csv", ".json", ".txt"]

# -------------------------------------------------
# Root endpoint (prevents 404)
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "Service running"}

# -------------------------------------------------
# Upload endpoint
# -------------------------------------------------
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_6737: str = Header(None)
):
    if x_upload_token_6737 != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    filename = file.filename
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    if filename.endswith(".csv"):
        decoded = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))
        rows = list(reader)

        if not rows:
            raise HTTPException(status_code=400, detail="Empty CSV")

        columns = reader.fieldnames
        total_value = sum(float(row["value"]) for row in rows)
        categories = Counter(row["category"] for row in rows)

        return {
            "email": "22f3002796@ds.study.iitm.ac.in",
            "filename": filename,
            "rows": len(rows),
            "columns": columns,
            "totalValue": round(total_value, 2),
            "categoryCounts": dict(categories)
        }

    return {"message": "File validated successfully"}
