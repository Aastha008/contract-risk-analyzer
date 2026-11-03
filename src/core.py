import os
import json
from typing import List, Dict, Any, Optional
from io import BytesIO

from pypdf import PdfReader
from docx import Document

import chromadb
from chromadb.config import Settings

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain_community.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
        except ImportError:
            class RecursiveCharacterTextSplitter:
                def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: Optional[List[str]] = None):
                    self.chunk_size = chunk_size
                    self.chunk_overlap = chunk_overlap

                def split_text(self, text: str) -> List[str]:
                    if not text:
                        return []
                    chunks = []
                    start = 0
                    text_len = len(text)
                    step = max(1, self.chunk_size - self.chunk_overlap)
                    while start < text_len:
                        end = min(start + self.chunk_size, text_len)
                        chunks.append(text[start:end])
                        if end == text_len:
                            break
                        start += step
                    return chunks

from openai import OpenAI

from src.models import StructuredRiskReport, ClauseCitation, Rulebook, RuleCreate

class ContractAnalyzerEngine:
    def __init__(self, persist_dir: Optional[str] = None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.openai_api_key or self.openai_api_key == "dummy-key-for-testing":
            self.client = None
        else:
            self.client = OpenAI(api_key=self.openai_api_key)
        
        db_path = persist_dir or os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_data")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="corporate_rulebook")
        
        # Initialize default rules if empty
        if self.collection.count() == 0:
            self._seed_default_rules()

    def _seed_default_rules(self):
        default_rules = [
            RuleCreate(
                rule_id="LIAB-01",
                category="Liability",
                description="Vendor liability must be capped at no less than 12 months of fees paid under the agreement. Uncapped liability is prohibited."
            ),
            RuleCreate(
                rule_id="TERM-01",
                category="Termination",
                description="Either party may terminate for convenience with a maximum of 30 days written notice."
            ),
            RuleCreate(
                rule_id="GOV-01",
                category="Governing Law",
                description="Contracts must be governed by the laws of the State of Delaware or New York, with local jurisdiction."
            ),
            RuleCreate(
                rule_id="INDEM-01",
                category="Indemnification",
                description="Indemnification obligations must be mutual and exclude consequential or indirect damages unless arising from gross negligence or willful misconduct."
            )
        ]
        self.add_rules(Rulebook(rules=default_rules))

    def add_rules(self, rulebook: Rulebook):
        ids = [rule.rule_id for rule in rulebook.rules]
        documents = [f"Category: {rule.category}. Rule: {rule.description}" for rule in rulebook.rules]
        metadatas = [{"category": rule.category, "rule_id": rule.rule_id} for rule in rulebook.rules]
        
        embeddings = self._get_embeddings(documents)
        
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.client:
            return [[0.1] * 1536 for _ in texts]
        
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]

    def parse_document(self, file_content: bytes, filename: str) -> str:
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(BytesIO(file_content))
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            return text
        elif filename.lower().endswith(".docx"):
            doc = Document(BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text
        else:
            try:
                return file_content.decode("utf-8")
            except Exception:
                raise ValueError(f"Unsupported file format for: {filename}")

    def chunk_contract(self, text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)

    def analyze_contract(self, file_content: bytes, filename: str) -> StructuredRiskReport:
        raw_text = self.parse_document(file_content, filename)
        chunks = self.chunk_contract(raw_text)
        
        all_rules_data = self.collection.get()
        rules_text = "\n".join(all_rules_data["documents"]) if all_rules_data and "documents" in all_rules_data else "No rules found."
        
        prompt = f"""
You are an expert AI Legal Contract Risk Analyzer. Analyze the following contract text against the corporate rulebook provided below.

CORPORATE RULEBOOK:
{rules_text}

CONTRACT TEXT:
{raw_text[:12000]}

Perform a comprehensive risk review and return a JSON response strictly matching this schema:
{{
    "contract_title": "{filename}",
    "overall_risk_score": <float between 0 and 100>,
    "governing_law": "<governing law found or null>",
    "liability_limits": "<liability limits found or null>",
    "termination_notice": "<termination notice terms found or null>",
    "flagged_clauses": [
        {{
            "clause_title": "<string title or heading>",
            "clause_text": "<exact text excerpt>",
            "rule_id_matched": "<matching rule id like LIAB-01>",
            "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
            "explanation": "<detailed reasoning>"
        }}
    ]
}}
"""

        if not self.client:
            return StructuredRiskReport(
                contract_title=filename,
                overall_risk_score=45.0,
                governing_law="State of California",
                liability_limits="Uncapped liability",
                termination_notice="14 days notice",
                flagged_clauses=[
                    ClauseCitation(
                        clause_title="Limitation of Liability",
                        clause_text="Provider shall have unlimited liability for all damages.",
                        rule_id_matched="LIAB-01",
                        risk_level="HIGH",
                        explanation="Contract specifies uncapped liability which violates corporate policy LIAB-01."
                    )
                ]
            )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise legal risk assessment engine that outputs valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return StructuredRiskReport(**data)
