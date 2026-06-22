# Fatora Facturx

تطبيق لانشاء فواتير PDF مدمجة مع XML بتاع ZATCA في ERPNext 15.

## المتطلبات
- ERPNext 15
- KSA Compliance App
- Python 3.10+

## التنصيب

### 1. نصب التطبيق
```bash
bench get-app fatora_facturx [repo_url]
bench --site [site_name] install-app fatora_facturx
```

### 2. نصب المكتبات
```bash
bash apps/fatora_facturx/install.sh [site_name]
```

مثال:
```bash
bash apps/fatora_facturx/install.sh erp.erpnext.support
```

## الاعدادات
روح Facturx Settings واختار:
- Single Format: تنسيق واحد - حدد التنسيق الافتراضي
- Multiple Formats: يظهر Dialog لاختيار التنسيق عند كل طباعة

## الاستخدام
1. افتح اي Sales Invoice مسبمتة
2. اضغط زرار Factur-X PDF
3. سيتم تحميل PDF مدمج مع XML تلقائيا

## هيكل التطبيق
fatora_facturx/

├── fatora_facturx/

│   ├── doctype/

│   │   ├── facturx_settings/

│   │   └── facturx_invoice/

│   ├── public/js/

│   │   └── sales_invoice.js

│   └── api.py

├── requirements.txt

├── install.sh

└── README.md

## المكتبات
- playwright: تحويل HTML الى PDF بجودة عالية
- pypdf: دمج XML جوا PDF
- factur-x: مكتبة Factur-X
