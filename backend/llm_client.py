import litellm
import base64
import json
import os
from dotenv import load_dotenv
load_dotenv()
def process_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    schema = {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "invoice_date": {"type": "string"},
            "due_date": {"type": "string"},
            "seller": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "tax_id": {"type": "string"}
                }
            },
            "buyer": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"}
                }
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"}
                    }
                }
            },
            "subtotal": {"type": "number"},
            "tax_rate": {"type": "number"},
            "tax_amount": {"type": "number"},
            "total_amount": {"type": "number"},
            "currency": {"type": "string"},
            "notes": {"type": "string"},
            "payment_terms": {"type": "string"}
        }
    }
    
    prompt = """You are an expert invoice data extraction assistant. Analyze this image and extract all invoice information.

The image may contain screenshots, handwritten notes, or digital documents.

Extract and structure the information. Return ONLY valid JSON following the provided schema.

If information is missing, use reasonable defaults or null values.
For dates, use ISO format (YYYY-MM-DD).
For prices, extract numerical values only."""
    
    try:
        response = litellm.completion(
            model="gemini/gemini-2.5-flash",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }],
            response_format={
                "type": "json_object",
                "response_schema": schema
            },
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        return data
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")
