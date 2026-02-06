from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
import subprocess
import pathlib
import os

router = APIRouter(tags=["dwg2dxf"])

BASE = pathlib.Path("/opt/dwg2dxf-api/tmp")

@router.post("/convert")
async def convert_dwg(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".dwg"):
        raise HTTPException(status_code=400, detail="Sadece DWG dosyaları kabul edilir.")

    job_id = str(uuid.uuid4())
    job_dir = BASE / job_id
    in_dir = job_dir / "in"
    out_dir = job_dir / "out"

    try:
        # exist_ok=True ekledik, klasör varsa hata vermez
        in_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        dwg_path = in_dir / file.filename
        content = await file.read()
        
        with open(dwg_path, "wb") as f:
            f.write(content)

        # Scripti çalıştır ve çıktıları yakala
        result = subprocess.run(
            ["/opt/dwg2dxf-api/oda.sh", str(in_dir), str(out_dir)],
            timeout=120,
            capture_output=True,
            text=True
        )

        # Eğer script hata kodu (returncode != 0) dönerse detayını göster
        if result.returncode != 0:
            print(f"ODA ERROR: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"Dönüştürme Hatası: {result.stderr}")

        dxf_files = list(out_dir.glob("*.dxf"))
        if not dxf_files:
            raise HTTPException(status_code=500, detail="DXF dosyası oluşturulamadı.")

        return FileResponse(
            dxf_files[0],
            media_type="application/dxf",
            filename=dxf_files[0].name
        )

    except Exception as e:
        print(f"Sistem Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
