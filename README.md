# Sports-PoS - Enterprise Retail Management System

A high-performance, dark-themed, serverless desktop Point of Sale (POS) and inventory management workspace engineered from scratch. The application replaces paper ledgers with robust SQL transactional guarantees, multi-row checkout padding, automated cost auditing, dynamic data visualizations, and an embedded administrative security layer.

## 🖥️ System Preview

![Main Dashboard Preview](./assets/mainDB.png)

## 🚀 Key Engineering Features

- **🏠 Dynamic Overview KPI Dashboard:** Monitors daily sales transaction volumes, manages responsive real-time layout elements, and uses an interactive low-stock warning metric card for automated storefront updates.
- **👁️ Privacy-Eye Cash Drawer Log Desk:** An expanded fiscal logging panel tracking Gross Revenue, Daily Shop Expenses, and True Net Profits behind a toggleable security mask layer.
- **🖨️ Automated Cashier Billing Pad:** Features live type-ahead catalog search filtering, instant discount and change calculations, automatic warehouse shelf subtractions, and programmatic multi-line A5 PDF invoice receipt generation via ReportLab.
- **📦 Comprehensive Inventory & Bulk Spreadsheet Ingestion:** Full inventory CRUD mechanics integrated with a multi-column Excel/CSV parser using Pandas to instantly merge incoming quantities into database records.
- **↩️ Structured Returns & Damaged Disposal Log:** Features dedicated prompt gates requiring documented return reasons, combined with a "Mark as Damaged" write-off utility that removes broken goods from inventory permanently.
- **🔑 Dynamic Admin Security Gate:** Restricts access to sensitive baseline margin grids using an updateable, secure SQL-driven configuration PIN setup with automated change auditing logs.
- **🛠️ Integrated SQL Developer Sandbox Terminal:** A built-in diagnostic layout built with macro templates that lets developers run raw SQL statement strings directly on-screen with dynamically generated query response trees.


## 🛠️ Technology Stack & Architecture

- **Core Programming Language:** Python 3.10+
- **GUI Desktop Engine:** CustomTkinter & Tkinter TTK Canvas Maps
- **Data Analytics Visualization:** Matplotlib Engine (Renders 7-day item movement velocity trends)
- **Persistent Storage Framework:** SQLite3 (Serverless, relational storage configuration)
- **External Data Parsers:** Pandas & OpenPyXL
- **Document Rendering Pipeline:** ReportLab (Compiles programmatic A5 layout receipts)

---

## 📂 Project Structure

```text
Sports-PoS/
│
├── main_dashboard.py       # Main Application Driver & UI Views
├── durrani_sports.db       # Embedded SQLite Relational Storage
├── requirements.txt        # Application Dependencies Layout
└── README.md               # Repository Documentation Manual
