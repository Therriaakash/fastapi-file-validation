from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import csv
import io
from collections import Counter

app = FastAPI()

# ---------------------------
# Enable CORS (important!)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# ---------------------------
# Constants
# ---------------------------
VALID_TOKEN = "2ki19djfqqs0zw00"
MAX_FILE_SIZE = 59 * 1024  # 59 KB
ALLOWED_EXTENSIONS = [".csv", ".json", ".txt"]

# ---------------------------
# Upload Endpoint
# ---------------------------
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_6737: str = Header(None)
):
    
    # 1️⃣ Authentication Check
    if x_upload_token_6737 != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2️⃣ File Extension Check
    filename = file.filename
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 3️⃣ File Size Check
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # Only analyze CSV files
    if filename.endswith(".csv"):

        decoded = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))

        rows = list(reader)
        if not rows:
            raise HTTPException(status_code=400, detail="Empty CSV")

        # Extract column names
        columns = reader.fieldnames

        # Compute totalValue
        total_value = sum(float(row["value"]) for row in rows)

        # Count categories
        categories = Counter(row["category"] for row in rows)

        return {
            "email": "22f3002796@ds.study.iitm.ac.in",
            "filename": filename,
            "rows": len(rows),
            "columns": columns,
            "totalValue": round(total_value, 2),
            "categoryCounts": categories
        }

    return {"message": "File validated successfully"}
