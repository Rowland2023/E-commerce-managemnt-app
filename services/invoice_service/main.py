from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from io import BytesIO

app = FastAPI(title="Invoice Generation Service")
@app.get("/") 
def root(): 
    return {"status": "success", "message": "Invoice API is live"} 

@app.get("/health") 
def health(): 
    return {"status": "ok"}

class InvoiceData(BaseModel):
    order_id: str
    customer_name: str
    amount: float
    items: list[dict] # list of {"name": str, "price": float}

@app.post("/generate-invoice/")
async def generate_invoice(data: InvoiceData):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # --- Draw Invoice Header ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "OFFICIAL INVOICE")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Order ID: {data.order_id}")
    p.drawString(100, 760, f"Customer: {data.customer_name}")
    p.drawString(100, 740, f"Total Amount: ${data.amount:.2f}")

    # --- Draw Items Table ---
    y_position = 700
    p.drawString(100, y_position, "Items:")
    y_position -= 20
    
    for item in data.items:
        p.drawString(120, y_position, f"- {item['name']}: ${item['price']:.2f}")
        y_position -= 20

    p.showPage()
    p.save()

    pdf_out = buffer.getvalue()
    buffer.close()

    return Response(
        content=pdf_out,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{data.order_id}.pdf"}
    )