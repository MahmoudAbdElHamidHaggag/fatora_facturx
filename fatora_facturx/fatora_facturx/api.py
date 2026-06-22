import frappe
from frappe import _
import io
import tempfile
import os

def get_pdf_with_chromium(invoice_name, print_format):
    from playwright.sync_api import sync_playwright
    
    # جيب الـ HTML من ERPNext
    html_content = frappe.get_print(
        "Sales Invoice",
        invoice_name,
        print_format=print_format
    )
    
    # جيب الـ site URL
    site_url = frappe.utils.get_url()
    
    # استبدل الـ relative paths بـ absolute URLs
    html_content = html_content.replace(
        'href="/', f'href="{site_url}/'
    ).replace(
        'src="/', f'src="{site_url}/'
    )
    
    # احفظ HTML مؤقت
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
        f.write(html_content)
        tmp_html = f.name
    
    tmp_pdf = tmp_html.replace('.html', '.pdf')
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = browser.new_page()
            page.goto(f'file://{tmp_html}', wait_until='networkidle', timeout=30000)
            page.pdf(
                path=tmp_pdf,
                format='A4',
                margin={"top": "6mm", "bottom": "6mm", "left": "6mm", "right": "6mm"},
                print_background=True
            )
            browser.close()
        
        with open(tmp_pdf, 'rb') as f:
            pdf_content = f.read()
        
        return pdf_content
    finally:
        if os.path.exists(tmp_html):
            os.unlink(tmp_html)
        if os.path.exists(tmp_pdf):
            os.unlink(tmp_pdf)


@frappe.whitelist()
def generate_facturx(invoice_name, print_format):
    additional_fields = frappe.get_all(
        "Sales Invoice Additional Fields",
        filters={"sales_invoice": invoice_name},
        fields=["name"],
        limit=1
    )
    
    if not additional_fields:
        frappe.throw(_("No ZATCA XML found for this invoice"))
    
    af_doc = frappe.get_doc("Sales Invoice Additional Fields", additional_fields[0].name)
    xml_content = af_doc.invoice_xml
    
    if not xml_content:
        frappe.throw(_("XML content is empty"))
    
    # جيب الـ PDF بـ Chromium
    pdf_content = get_pdf_with_chromium(invoice_name, print_format)
    
    # ادمج XML جوا PDF
    from pypdf import PdfWriter, PdfReader
    
    reader = PdfReader(io.BytesIO(pdf_content))
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    writer.add_attachment("factur-x.xml", xml_content.encode("utf-8"))
    
    output = io.BytesIO()
    writer.write(output)
    merged_content = output.getvalue()
    
    # امسح القديم لو موجود
    existing_fx = frappe.get_all(
        "Facturx Invoice",
        filters={"sales_invoice": invoice_name},
        fields=["name", "merged_pdf"],
        limit=1
    )
    
    if existing_fx and existing_fx[0].merged_pdf:
        try:
            old_file = frappe.get_all(
                "File",
                filters={"file_url": existing_fx[0].merged_pdf},
                fields=["name"],
                limit=1
            )
            if old_file:
                frappe.delete_doc("File", old_file[0].name, ignore_permissions=True)
        except Exception:
            pass
    
    file_name = f"{invoice_name} \u2726.pdf"
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": merged_content,
        "is_private": 0
    })
    file_doc.insert(ignore_permissions=True)
    
    if existing_fx:
        fx_doc = frappe.get_doc("Facturx Invoice", existing_fx[0].name)
        fx_doc.print_format_used = print_format
        fx_doc.merged_pdf = file_doc.file_url
        fx_doc.save(ignore_permissions=True)
    else:
        fx_doc = frappe.get_doc({
            "doctype": "Facturx Invoice",
            "sales_invoice": invoice_name,
            "print_format_used": print_format,
            "merged_pdf": file_doc.file_url
        })
        fx_doc.insert(ignore_permissions=True)
    
    frappe.db.commit()
    
    return {
        "file_url": file_doc.file_url,
        "file_name": file_name
    }


@frappe.whitelist()
def get_settings():
    settings = frappe.get_single("Facturx Settings")
    return {
        "mode": settings.mode,
        "default_print_format": settings.default_print_format
    }
