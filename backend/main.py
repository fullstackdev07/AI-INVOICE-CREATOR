# backend/main.py

import os
import json
import csv
import io
import openai
from dotenv import load_dotenv
from typing import List, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from dicttoxml import dicttoxml
from weasyprint import HTML, CSS # <-- Import the new library

# --- Initial Setup ---
load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173","http://0.0.0.0:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("FATAL ERROR: OPENAI_API_KEY environment variable not set!")
openai.api_key = openai_api_key

# --- Pydantic Models ---
class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
class InvoiceStructure(BaseModel):
    title: str
    company_name: str
    company_address: str
    bill_to_name: str
    bill_to_address: str
    invoice_number: str
    date: str
    due_date: str
    items: List[InvoiceItem]
    notes: Optional[str] = None
    tax_rate: Optional[float] = Field(None, description="Tax rate as a percentage, e.g., 10 for 10%")
    logo_url: Optional[str] = None
    theme_color: str
class ExportFormat(str, Enum):
    pdf = "pdf"
    xml = "xml"
    json = "json"
    csv = "csv"

# --- API Endpoints ---
@app.post("/api/generate-template", response_model=InvoiceStructure)
async def generate_template(prompt: str):
    system_prompt = f"""
    You are an expert invoice JSON generator. Your task is to generate a JSON object containing placeholder data for an invoice.
    The user's request is: "{prompt}"

    You MUST follow this exact JSON structure and format. Do not add or remove fields.
    EXAMPLE STRUCTURE:
    {{
      "title": "Invoice",
      "company_name": "Your Company LLC",
      "company_address": "123 Main St\\nCity, State 12345",
      "bill_to_name": "Client Name",
      "bill_to_address": "456 Client Ave\\nClient City, ST 54321",
      "invoice_number": "INV-001",
      "date": "YYYY-MM-DD",
      "due_date": "YYYY-MM-DD",
      "items": [
        {{
          "description": "Service or Product Description",
          "quantity": 1,
          "unit_price": 100.00
        }}
      ],
      "notes": "Thank you for your business.",
      "tax_rate": 8.5,
      "logo_url": null,
      "theme_color": "#3498db"
    }}

    - Populate the fields with realistic data based on the user's request: "{prompt}".
    - For dates, use a format like YYYY-MM-DD.
    - If the user's prompt mentions "tax", provide a number for `tax_rate`. Otherwise, use null.
    - If the user's prompt mentions a "logo", provide a placeholder URL for `logo_url`. Otherwise, use null.
    - Respond ONLY with the raw JSON object. Do not add explanations or markdown.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"}
        )
        response_content = response.choices[0].message.content
        print("--- OpenAI Response ---"); print(response_content); print("-----------------------")
        try:
            parsed_json = json.loads(response_content)
            validated_data = InvoiceStructure.model_validate(parsed_json)
            return validated_data
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Validation failed after getting response from AI: {e}")
            raise HTTPException(status_code=500, detail="The AI returned a malformed response. Please try again.")
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
        raise HTTPException(status_code=502, detail=f"OpenAI API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/api/export")
async def export_invoice(invoice: InvoiceStructure, format: ExportFormat):
    if format == ExportFormat.json:
        return JSONResponse(content=invoice.model_dump(), headers={"Content-Disposition": "attachment; filename=invoice.json"})
    if format == ExportFormat.xml:
        xml_data = dicttoxml(invoice.model_dump(), custom_root='invoice', attr_type=False)
        return Response(content=xml_data, media_type="application/xml", headers={"Content-Disposition": "attachment; filename=invoice.xml"})
    if format == ExportFormat.csv:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Description', 'Quantity', 'Unit Price', 'Total'])
        for item in invoice.items:
            writer.writerow([item.description, item.quantity, item.unit_price, item.quantity * item.unit_price])
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=invoice_items.csv"})
    
    if format == ExportFormat.pdf:
        # --- PDF GENERATION USING WEASYPRINT (THE FIX) ---
        subtotal = sum(item.quantity * item.unit_price for item in invoice.items)
        tax_amount = (subtotal * (invoice.tax_rate / 100)) if invoice.tax_rate is not None else 0
        total = subtotal + tax_amount

        html_template = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: sans-serif; color: #333; }}
                    .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, .15); font-size: 16px; line-height: 24px; }}
                    .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }}
                    .header h1 {{ margin: 0; color: {invoice.theme_color}; }}
                    .details-flex {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; }}
                    .invoice-details {{ text-align: right; }}
                    .item-table {{ width: 100%; border-collapse: collapse; text-align: left; }}
                    .item-table th, .item-table td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                    .item-table .heading {{ background: #f5f5f5; font-weight: bold; }}
                    .text-right {{ text-align: right; }}
                    .totals {{ text-align: right; margin-top: 20px; }}
                    .totals p {{ margin: 5px 0; }}
                    .total-amount {{ font-size: 1.2em; color: {invoice.theme_color}; font-weight: bold; }}
                    .notes {{ margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="invoice-box">
                    <div class="header">
                        <div>
                            <h2 style="font-size: 2em; margin-bottom: 0;">{invoice.company_name}</h2>
                            <p>{invoice.company_address.replace('\\n', '<br>')}</p>
                        </div>
                        <h1 style="font-size: 2.5em;">{invoice.title.upper()}</h1>
                    </div>
                    <div class="details-flex">
                        <div>
                            <strong>Bill To:</strong><br>
                            {invoice.bill_to_name}<br>
                            {invoice.bill_to_address.replace('\\n', '<br>')}
                        </div>
                        <div class="invoice-details">
                            <strong>Invoice #:</strong> {invoice.invoice_number}<br>
                            <strong>Date:</strong> {invoice.date}<br>
                            <strong>Due Date:</strong> {invoice.due_date}
                        </div>
                    </div>
                    <table class="item-table">
                        <tr class="heading">
                            <th>Item</th><th style="width: 15%;">Qty</th><th style="width: 20%;">Unit Price</th><th class="text-right">Total</th>
                        </tr>
                        {''.join(f"<tr><td>{item.description}</td><td>{item.quantity}</td><td>${item.unit_price:.2f}</td><td class='text-right'>${(item.quantity * item.unit_price):.2f}</td></tr>" for item in invoice.items)}
                    </table>
                    <div class="totals">
                        <p><strong>Subtotal:</strong> ${subtotal:.2f}</p>
                        {f'<p><strong>Tax ({invoice.tax_rate}%):</strong> ${tax_amount:.2f}</p>' if invoice.tax_rate is not None else ''}
                        <p class="total-amount">Total: ${total:.2f}</p>
                    </div>
                    {f'<div class="notes"><strong>Notes:</strong><p>{invoice.notes}</p></div>' if invoice.notes else ''}
                </div>
            </body>
        </html>
        """
        
        pdf_bytes = HTML(string=html_template).write_pdf()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"}
        )