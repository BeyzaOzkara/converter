#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import dwg2dxf 
from . import pdf2dxf

app = FastAPI(
    title="DWG to DXF API",
    # root_path kullanmıyoruz çünkü Nginx zaten yolu temizleyip gönderiyor
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dwg2dxf.router)
app.include_router(pdf2dxf.router)
