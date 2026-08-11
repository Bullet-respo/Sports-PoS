# 🏢 Sports-PoS — Enterprise Point of Sale & Smart Inventory Analytics

**Sports-PoS** is an enterprise-grade, dark-themed, serverless desktop **Point of Sale (POS) and Inventory Management System** designed for retail businesses.

Built from scratch using **Python, SQLite, and CustomTkinter**, the system provides a complete workspace for managing sales, inventory, returns, expenses, profits, receipts, and administrative operations.

The application also includes hardware-bound licensing, automated cost auditing, data visualization, and an integrated administrative security layer.

---

## 🚀 Key Features

### 🔒 Hardware-Bound Activation System

Sports-PoS includes a hardware-locked licensing framework that binds activation keys to the machine's motherboard/CPU hardware UUID (HWID).

Features include:

- Hardware-based license validation
- HWID-based activation
- Integrated clipboard copy utility
- Client-specific activation key generation
- Protection against unauthorized software distribution

> ⚠️ The license key can be retrieved only from the administrator. Contact affang1122@gmail.com for the licence key.

---

### 📊 Dynamic Overview KPI Dashboard

The dashboard provides a centralized overview of the store's current performance.

It monitors:

- Daily transaction counts
- Low-stock alerts
- Sales activity
- Real-time sales trends
- Key business performance indicators

---

### 👁️ Privacy-Eye Cash Drawer Log Desk

A privacy-focused financial monitoring section provides controlled access to sensitive shop financial information.

It displays:

- Gross Revenue
- Daily Shop Expenses
- True Net Profit Margins

The privacy shield can be toggled when sensitive financial information needs to be hidden.

---

### 🧾 Automated Cashier Billing Pad

The integrated billing system provides a complete checkout workflow.

Features include:

- Live product/catalog search
- Real-time filtering
- Multi-line checkout
- Automatic discount calculations
- Automatic change calculations
- Automatic inventory subtraction
- Automated receipt generation
- A5 PDF receipt generation using ReportLab

---

### 📦 Inventory Management & Excel Bulk Import

The inventory module provides comprehensive stock management.

Supported operations include:

- Create products
- Read product information
- Update inventory
- Delete products
- Stock management
- Automated spreadsheet import
- Excel-based bulk product ingestion

The system uses **Pandas** and **OpenPyXL** for spreadsheet processing.

---

### ↩️ Returns & Damaged Goods Management

Sports-PoS provides structured handling of returned and damaged products.

Features include:

- Product return management
- Required return-reason prompts
- Return tracking
- Damaged product handling
- "Mark as Damaged" functionality
- Permanent write-off of unsellable inventory

---

### 🔑 Persistent Admin Vault

Sensitive business information is protected through an administrative security layer.

The Admin Vault restricts access to:

- Wholesale cost prices
- Profit margin information
- Sensitive financial tables

The system uses a **database-driven security PIN** with automated change logging.

---

### 🛠️ Integrated SQL Sandbox Terminal

Developers and administrators can access an integrated SQL console.

The terminal supports:

- Raw SQL query execution
- SQL macro templates
- Sandboxed database queries
- Dynamic query response rendering
- Grid-based result visualization

This provides a convenient way to inspect and interact with the SQLite database during development and administration.

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **CustomTkinter** | Modern desktop GUI |
| **Tkinter TTK** | GUI widgets and interface components |
| **SQLite3** | Serverless relational database |
| **Matplotlib** | Data visualization and sales charts |
| **Pandas** | Data processing and spreadsheet handling |
| **OpenPyXL** | Excel file import/export processing |
| **ReportLab** | A5 PDF receipt generation |

The system uses a **serverless architecture**, with SQLite providing local relational data storage.

---

# 📂 Project Structure

```text
Sports-PoS/
│
├── Images/
│
├── main_dashboard.py
│   └── Main application GUI and controller logic
│
├── initialize_database.py
│   └── Database schema and initialization setup
│
├── durrani_sports.db
│   └── Embedded SQLite database
│
├── requirements.txt
│   └── Python application dependencies
│
├── README.md
│   └── Project documentation
│
└── .gitignore
    └── Files excluded from version control
```
---

### 💻 Installation & Setup

1. Clone the Repository
   > git clone https://github.com/Bullet-respo/Sports-PoS.git
   > cd Sports-PoS

2. Install Dependencies
   > pip install -r requirements.txt

3. Initialize the Database
   > python initialize_database.py

4. Launch Sports-PoS
   > python main_dashboard.py

---

### 🔐 Security & Licensing

Sports-PoS includes multiple security mechanisms designed to protect sensitive business and licensing information.

Hardware-Based Licensing

Activation keys are associated with a machine-specific Hardware ID (HWID) derived from motherboard/CPU hardware information.

Administrative Security

Sensitive wholesale prices and profit information are protected through the application's Admin Vault.

Developer SQL Access

The integrated SQL Sandbox Terminal provides controlled access to database operations for development and administration.

---

### Default Credentials
  - Hidden Admin Panel PIN code: 0000
  - Developer Console PassWord: Admin
