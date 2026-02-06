from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
import subprocess
import pathlib
import os
import ezdxf
from ezdxf import path # 1.4.3 için doğru modül

router = APIRouter(tags=["pdf2dxf"])
BASE = pathlib.Path("/opt/dwg2dxf-api/tmp")

def heal_dxf(dxf_file_path, tolerance=0.1):
    """
    DXF içindeki kopuk LINE ve ARC objelerini birleştirip kapalı Polyline yapar.
    ezdxf 1.4.3+ sürümü için modernize edilmiştir.
    """
    try:
        doc = ezdxf.readfile(dxf_file_path)
        msp = doc.modelspace()
        
        # 1. Tüm Çizgi (LINE) ve Yay (ARC) objelerini seç
        entities = msp.query('LINE ARC')
        if not entities:
            return

        # 2. Objeleri 'Path' nesnelerine dönüştür
        paths = path.from_entities(entities)
        
        # 3. Yolları belirlenen tolerans ile birleştir (Join)
        # Bu işlem kopuk uçları birbirine bağlar
        joined_paths = path.join_paths(paths, tolerance=tolerance)
        
        # 4. Eski dağınık çizgileri temizle
        for e in entities:
            msp.delete_entity(e)
            
        # 5. Birleştirilmiş yolları Polyline olarak tekrar çiz
        # Bu fonksiyon kapalı olanları otomatik olarak 'Closed' işaretler
        path.render_lwpolylines(msp, joined_paths, distance=tolerance)
        
        doc.save()
        print(f"DEBUG: Heal islemi (v1.4.3) basariyla tamamlandi: {dxf_file_path}")
    except Exception as e:
        print(f"ERROR: Heal hatasi: {str(e)}")

def is_vector_pdf(pdf_path: str) -> bool:
    try:
        result = subprocess.run(
            ["mutool", "draw", "-F", "trace", str(pdf_path), "1"],
            capture_output=True, text=True, check=True
        )
        output = result.stdout.lower()
        vector_indicators = ["<path", "<fill_path", "<stroke_path", "<text", "<char"]
        return any(ind in output for ind in vector_indicators)
    except Exception:
        return False

@router.post("/convert-pdf") 
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyaları kabul edilir.")

    job_id = str(uuid.uuid4())
    job_dir = BASE / job_id
    in_dir = job_dir / "in"
    out_dir = job_dir / "out"

    try:
        in_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = in_dir / file.filename
        svg_path = out_dir / "temp.svg"
        dxf_path = out_dir / f"{pathlib.Path(file.filename).stem}.dxf"

        content = await file.read()
        with open(pdf_path, "wb") as f:
            f.write(content)

        if not is_vector_pdf(pdf_path):
            raise HTTPException(status_code=400, detail="PDF vektörel veri içermiyor.")

        # PDF -> SVG
        subprocess.run(["mutool", "draw", "-o", str(svg_path), str(pdf_path), "1"], check=True)
        if not svg_path.exists() and (out_dir / "temp1.svg").exists():
            (out_dir / "temp1.svg").rename(svg_path)

        # SVG -> DXF
        env = os.environ.copy()
        env["HOME"] = "/tmp"
        subprocess.run(
            ["inkscape", "--export-type=dxf", f"--export-filename={str(dxf_path)}", "--export-dpi=96", str(svg_path)],
            check=True, capture_output=True, env=env
        )

        # HEAL İşlemi
        if dxf_path.exists():
            heal_dxf(str(dxf_path), tolerance=0.1)
        else:
            raise Exception("DXF dosyasi olusturulamadi.")

        return FileResponse(path=dxf_path, media_type="application/dxf", filename=dxf_path.name)

    except Exception as e:
        print(f"Sistem Hatası (PDF): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
