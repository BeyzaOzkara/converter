from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
import subprocess
import pathlib
import shutil

router = APIRouter(prefix="/dwg2dxf", tags=["dwg2dxf"])
BASE = pathlib.Path("/opt/dwg2dxf-api/tmp")

@router.post("/convert")
async def convert_dwg(file: UploadFile = File(...)):
    # Sadece .dwg dosyalarını kabul et
    if not file.filename.lower().endswith(".dwg"):
        raise HTTPException(status_code=400, detail="Sadece DWG dosyaları kabul edilir.")

    job_id = str(uuid.uuid4())
    job_dir = BASE / job_id
    in_dir = job_dir / "in"
    out_dir = job_dir / "out"

    try:
        in_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        dwg_path = in_dir / file.filename
        
        # Dosyayı diske yaz
        with open(dwg_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Dönüştürme işlemini çalıştır
        result = subprocess.run(
            ["/opt/dwg2dxf-api/oda.sh", str(in_dir), str(out_dir)],
            timeout=120,
            capture_output=True,
            text=True
        )

        # Çıktı klasöründe .dxf dosyasını bul
        dxf_files = list(out_dir.glob("*.dxf"))
        if not dxf_files:
            raise HTTPException(status_code=500, detail="Dönüştürme başarısız oldu.")

        return FileResponse(
            dxf_files[0],
            media_type="application/dxf",
            filename=dxf_files[0].name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Opsiyonel: İşlem bitince tmp klasörünü temizleme mekanizması eklenebilir.
