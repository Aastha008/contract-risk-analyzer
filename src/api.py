from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.models import StructuredRiskReport, AnalysisResponse, Rulebook, RuleCreate
from src.core import ContractAnalyzerEngine

app = FastAPI(
    title="Contract Risk Analyzer",
    description="Automated legal document review service evaluating contracts against custom compliance rules using RAG.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine singleton
engine = ContractAnalyzerEngine()

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "Contract Risk Analyzer"}

@app.post("/api/v1/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_contract(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    try:
        report = engine.analyze_contract(contents, file.filename)
        return AnalysisResponse(status="success", report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing contract: {str(e)}")

@app.post("/api/v1/rules", tags=["Rulebook"])
async def update_rulebook(rulebook: Rulebook):
    try:
        engine.add_rules(rulebook)
        return {"status": "success", "message": f"Successfully updated/added {len(rulebook.rules)} rules."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating rulebook: {str(e)}")

@app.get("/api/v1/rules", tags=["Rulebook"])
async def get_rulebook():
    try:
        all_data = engine.collection.get()
        rules = []
        if all_data and "ids" in all_data:
            for r_id, doc, meta in zip(all_data["ids"], all_data["documents"], all_data["metadatas"]):
                rules.append({
                    "rule_id": r_id,
                    "category": meta.get("category", "General"),
                    "description": doc
                })
        return {"rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rules: {str(e)}")
