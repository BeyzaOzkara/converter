from fastapi import FastAPI
# Ana dizindeki dwg2dxf.py dosyasını içe aktarıyoruz
from .dwg2dxf import router as converter_router

app = FastAPI(title="DWG to DXF Converter")

# Sadece ihtiyacın olan router'ı ekliyoruz
app.include_router(converter_router)

@app.get("/")
async def root():
    return {"message": "DWG to DXF API is running"}
