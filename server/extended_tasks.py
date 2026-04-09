"""
Extended tasks for DocForge v2.
Each task has a 'task_type' field for specialized grading.
Types: basic, confidence, schema_free, cross_doc, temporal, pii, table, adversarial, hierarchical
"""

EXTENDED_TASKS = [
    # 1. MULTILINGUAL — German invoice
    {
        "task_id": "multi_de_01", "difficulty": "medium", "task_type": "basic",
        "raw_text": (
            "RECHNUNG Nr. RE-2026-0847\nDatum: 12. Marz 2026\nFallig: 11. April 2026\n\n"
            "Lieferant: Braun & Vogel Maschinenbau GmbH\nIndustriestr. 78, 70565 Stuttgart\n"
            "USt-IdNr.: DE283947561\n\nKunde: Precision Tools AG\n"
            "Ansprechpartner: Markus Lehmann, Einkauf\nBahnhofstr. 14, 8001 Zurich, Schweiz\n\n"
            "Positionen:\n1. CNC-Fraserkopf FK-200 — 3 St. @ EUR 1.250,00 = EUR 3.750,00\n"
            "2. Kuhlmittelschlauch KS-50 (5m) — 10 St. @ EUR 45,00 = EUR 450,00\n"
            "3. Montageservice (vor Ort) — pauschal = EUR 800,00\n\n"
            "Nettobetrag: EUR 5.000,00\nMwSt. (19%): EUR 950,00\nGesamtbetrag: EUR 5.950,00"
        ),
        "schema_description": (
            "Extract: invoice_number, invoice_date, due_date, vendor_name, vendor_address, "
            "vendor_tax_id, client_name, client_contact, client_address, "
            "line_items (list: description, quantity, unit_price, total), "
            "subtotal, tax_rate, tax_amount, total_due"
        ),
        "gold_labels": {
            "invoice_number": "RE-2026-0847", "invoice_date": "12. Marz 2026",
            "due_date": "11. April 2026", "vendor_name": "Braun & Vogel Maschinenbau GmbH",
            "vendor_address": "Industriestr. 78, 70565 Stuttgart",
            "vendor_tax_id": "DE283947561", "client_name": "Precision Tools AG",
            "client_contact": "Markus Lehmann",
            "client_address": "Bahnhofstr. 14, 8001 Zurich, Schweiz",
            "line_items": [
                {"description": "CNC-Fraserkopf FK-200", "quantity": 3, "unit_price": 1250.0, "total": 3750.0},
                {"description": "Kuhlmittelschlauch KS-50 (5m)", "quantity": 10, "unit_price": 45.0, "total": 450.0},
                {"description": "Montageservice (vor Ort)", "quantity": 1, "unit_price": 800.0, "total": 800.0},
            ],
            "subtotal": 5000.0, "tax_rate": 19.0, "tax_amount": 950.0, "total_due": 5950.0,
        },
    },
    # 1b. MULTILINGUAL — Japanese receipt
    {
        "task_id": "multi_ja_01", "difficulty": "hard", "task_type": "basic",
        "raw_text": (
            "領収書\n鈴木ラーメン 本店\n東京都渋谷区神宮前3-12-8\nTEL: 03-5555-8821\n\n"
            "日付: 2026年3月20日 19:45\n担当: 田中\n\n"
            "味噌ラーメン (大盛)     ¥1,100\n醤油ラーメン            ¥900\n"
            "餃子 (6個) x2           ¥1,200\n枝豆                    ¥400\n"
            "生ビール x3             ¥1,800\n\n小計: ¥5,400\n消費税 (10%): ¥540\n合計: ¥5,940\n\n"
            "Visa *4821 決済済み"
        ),
        "schema_description": (
            "Extract: store_name, store_address, store_phone, date, server_name, "
            "line_items (list: item_name, quantity, total), "
            "subtotal, tax_rate, tax_amount, total, payment_method"
        ),
        "gold_labels": {
            "store_name": "鈴木ラーメン 本店", "store_address": "東京都渋谷区神宮前3-12-8",
            "store_phone": "03-5555-8821", "date": "2026年3月20日", "server_name": "田中",
            "line_items": [
                {"item_name": "味噌ラーメン (大盛)", "quantity": 1, "total": 1100},
                {"item_name": "醤油ラーメン", "quantity": 1, "total": 900},
                {"item_name": "餃子 (6個)", "quantity": 2, "total": 1200},
                {"item_name": "枝豆", "quantity": 1, "total": 400},
                {"item_name": "生ビール", "quantity": 3, "total": 1800},
            ],
            "subtotal": 5400, "tax_rate": 10.0, "tax_amount": 540, "total": 5940,
            "payment_method": "Visa ending 4821",
        },
    },
    # 1c. MULTILINGUAL — Spanish job posting
    {
        "task_id": "multi_es_01", "difficulty": "medium", "task_type": "basic",
        "raw_text": (
            "OFERTA DE EMPLEO — Ingeniero de Datos Senior\n"
            "Empresa: DataFlow Soluciones S.L., Madrid, Espana\n"
            "Modalidad: Hibrido (2 dias en oficina)\n"
            "Salario: EUR 55.000 - EUR 72.000 brutos anuales + bonus variable\n\n"
            "Requisitos: 5+ anos con Apache Spark o Databricks, SQL y Python avanzado, "
            "experiencia con AWS o GCP, titulo en Informatica o Ingenieria.\n"
            "Valorable: certificacion AWS, experiencia con dbt o Airflow.\n"
            "Beneficios: seguro medico, presupuesto formacion EUR 2.000/ano, "
            "25 dias vacaciones, horario flexible.\n"
            "Fecha limite: 15 de mayo de 2026."
        ),
        "schema_description": (
            "Extract: job_title, company, location, employment_type, salary_min, salary_max, "
            "salary_currency, required_skills (list), preferred_skills (list), "
            "benefits (list), remote_policy, application_deadline"
        ),
        "gold_labels": {
            "job_title": "Ingeniero de Datos Senior", "company": "DataFlow Soluciones S.L.",
            "location": "Madrid, Espana", "employment_type": "full-time",
            "salary_min": 55000, "salary_max": 72000, "salary_currency": "EUR",
            "required_skills": ["Apache Spark or Databricks", "SQL", "Python", "AWS or GCP"],
            "preferred_skills": ["AWS certification", "dbt", "Airflow"],
            "benefits": ["seguro medico", "presupuesto formacion", "25 dias vacaciones", "horario flexible"],
            "remote_policy": "hybrid", "application_deadline": "15 de mayo de 2026",
        },
    },

    # 2. CROSS-DOCUMENT RECONCILIATION
    {
        "task_id": "crossdoc_01", "difficulty": "hard", "task_type": "cross_doc",
        "raw_text": (
            "=== DOCUMENT A: PURCHASE ORDER ===\nPO #PO-9921\nDate: March 1, 2026\n"
            "From: Redwood Manufacturing Inc.\nTo: Atlas Supply Co.\n\n"
            "Ordered:\n1. Steel Plate A36 (10mm) — 200 units @ $85.00 = $17,000.00\n"
            "2. Copper Wire 12AWG — 500m @ $3.20/m = $1,600.00\n"
            "3. Rubber Gasket RG-44 — 1,000 pcs @ $0.75 = $750.00\n"
            "PO Total: $19,350.00\nDelivery: March 20, 2026\n\n"
            "=== DOCUMENT B: INVOICE ===\nInvoice #INV-6682\nDate: March 22, 2026\n"
            "From: Atlas Supply Co.\nTo: Redwood Manufacturing Inc.\n\n"
            "Shipped:\n1. Steel Plate A36 (10mm) — 200 units @ $87.50 = $17,500.00\n"
            "2. Copper Wire 12AWG — 450m @ $3.20/m = $1,440.00\n"
            "3. Rubber Gasket RG-44 — 1,000 pcs @ $0.75 = $750.00\n"
            "Invoice Total: $19,690.00\nDue: April 21, 2026"
        ),
        "schema_description": (
            "Compare PO and Invoice. Extract: po_number, invoice_number, po_total, invoice_total, "
            "discrepancies (list: field, po_value, invoice_value, description)"
        ),
        "gold_labels": {
            "po_number": "PO-9921", "invoice_number": "INV-6682",
            "po_total": 19350.0, "invoice_total": 19690.0,
            "discrepancies": [
                {"field": "Steel Plate unit_price", "po_value": "85.00", "invoice_value": "87.50", "description": "Unit price increased"},
                {"field": "Copper Wire quantity", "po_value": "500m", "invoice_value": "450m", "description": "Quantity reduced"},
                {"field": "total", "po_value": "19350.00", "invoice_value": "19690.00", "description": "Totals differ"},
            ],
        },
    },
    {
        "task_id": "crossdoc_02", "difficulty": "hard", "task_type": "cross_doc",
        "raw_text": (
            "=== DOCUMENT A: CONTRACT ===\nContract #CTR-2026-114\n"
            "Client: Pinnacle Ventures LLC\nVendor: Apex Consulting Group\n"
            "Monthly retainer: $15,000\nOvertime rate: $200/hr\nPayment terms: Net 15\n\n"
            "=== DOCUMENT B: INVOICE ===\nInvoice #AC-0342\nDate: March 1, 2026\n"
            "From: Apex Consulting Group\nTo: Pinnacle Ventures LLC\n\n"
            "1. Monthly retainer — $15,000.00\n2. Overtime: 12 hrs @ $225/hr — $2,700.00\n"
            "3. Travel expenses — $1,200.00\nTotal: $18,900.00\nTerms: Net 30"
        ),
        "schema_description": (
            "Compare Contract and Invoice. Extract: contract_number, invoice_number, "
            "contract_monthly, invoice_total, "
            "discrepancies (list: field, contract_value, invoice_value, description)"
        ),
        "gold_labels": {
            "contract_number": "CTR-2026-114", "invoice_number": "AC-0342",
            "contract_monthly": 15000.0, "invoice_total": 18900.0,
            "discrepancies": [
                {"field": "overtime_rate", "contract_value": "$200/hr", "invoice_value": "$225/hr", "description": "Rate mismatch"},
                {"field": "payment_terms", "contract_value": "Net 15", "invoice_value": "Net 30", "description": "Terms mismatch"},
                {"field": "travel_expenses", "contract_value": "not specified", "invoice_value": "$1,200.00", "description": "Not in contract"},
            ],
        },
    },

    # 3. CONFIDENCE CALIBRATION
    {
        "task_id": "confidence_01", "difficulty": "medium", "task_type": "confidence",
        "raw_text": (
            "From: j.morrison@████████.com\nSubject: Meeting follow-up\n\n"
            "Hi team, quick notes from today's call with [REDACTED] at NovaStar:\n"
            "- Budget approved for Q3: somewhere between $40K-$60K\n"
            "- Timeline: aiming for September but could slip to October\n"
            "- Main contact going forward: either James or his colleague Sarah\n"
            "- Their office is in Boston or maybe Cambridge, need to confirm\n\n"
            "Also, the project code is NS-2026-██ (I'll find the full number)\n\n"
            "Best,\nJordan Morrison\nProduct Lead, Vertex Solutions\nTel: (617) 555-0142"
        ),
        "schema_description": (
            "Extract with CONFIDENCE. Return JSON where each field has 'value' and "
            "'confidence' (0.0-1.0). Fields: sender_name, sender_email, sender_title, "
            "sender_company, sender_phone, client_company, budget_min, budget_max, "
            "timeline, primary_contact, office_city, project_code. "
            "LOW confidence for redacted/ambiguous, HIGH for clear fields."
        ),
        "gold_labels": {
            "sender_name": {"value": "Jordan Morrison", "confidence_expected": "high"},
            "sender_email": {"value": "j.morrison@unknown.com", "confidence_expected": "low"},
            "sender_title": {"value": "Product Lead", "confidence_expected": "high"},
            "sender_company": {"value": "Vertex Solutions", "confidence_expected": "high"},
            "sender_phone": {"value": "(617) 555-0142", "confidence_expected": "high"},
            "client_company": {"value": "NovaStar", "confidence_expected": "high"},
            "budget_min": {"value": 40000, "confidence_expected": "medium"},
            "budget_max": {"value": 60000, "confidence_expected": "medium"},
            "timeline": {"value": "September 2026", "confidence_expected": "medium"},
            "primary_contact": {"value": "James", "confidence_expected": "low"},
            "office_city": {"value": "Boston", "confidence_expected": "low"},
            "project_code": {"value": "NS-2026", "confidence_expected": "low"},
        },
    },

    # 4. SCHEMA-FREE DISCOVERY
    {
        "task_id": "schemafree_01", "difficulty": "hard", "task_type": "schema_free",
        "raw_text": (
            "EVENT CONFIRMATION\n\nDear Ms. Okonkwo,\n\n"
            "We confirm your reservation for the Annual Biotech Leadership Summit.\n\n"
            "Date: June 14-16, 2026\nVenue: The Ritz-Carlton, Half Moon Bay, CA\n"
            "Registration ID: BLS-2026-4471\n"
            "Badge: Dr. Amara Okonkwo, Chief Science Officer, Helix Therapeutics\n"
            "Dietary: Vegetarian\nTrack: Genomics & Precision Medicine\n\n"
            "Room: King Suite, ocean view. June 13-17. $485/night. Confirmation #RZ-881204.\n"
            "Shuttle from SFO at 3 PM June 13.\nGala dinner: June 15, 7:30 PM, Grand Ballroom.\n\n"
            "Contact: events@biotechsummit.org / (650) 555-0199"
        ),
        "schema_description": (
            "NO SCHEMA PROVIDED. Analyze the document and extract ALL structured "
            "information you can identify. Return a JSON object with descriptive field names."
        ),
        "gold_labels": {
            "event_name": "Annual Biotech Leadership Summit",
            "attendee_name": "Dr. Amara Okonkwo",
            "attendee_title": "Chief Science Officer",
            "attendee_company": "Helix Therapeutics",
            "event_dates": "June 14-16, 2026",
            "venue": "The Ritz-Carlton, Half Moon Bay, CA",
            "registration_id": "BLS-2026-4471",
            "dietary_preference": "Vegetarian",
            "session_track": "Genomics & Precision Medicine",
            "hotel_room_type": "King Suite, ocean view",
            "hotel_dates": "June 13-17",
            "hotel_rate": 485,
            "hotel_confirmation": "RZ-881204",
            "contact_email": "events@biotechsummit.org",
            "contact_phone": "(650) 555-0199",
        },
    },

    # 5. TEMPORAL REASONING
    {
        "task_id": "temporal_01", "difficulty": "hard", "task_type": "temporal",
        "raw_text": (
            "LEASE AGREEMENT SUMMARY\nTenant: Brightline Coworking LLC\n"
            "Landlord: Metropolitan Realty Trust\n"
            "Property: Suite 400-402, 180 N. Michigan Ave, Chicago IL 60601\n\n"
            "Lease commencement: April 1, 2024\nLease term: 36 months\n"
            "Monthly rent: $12,500 (increases 3% annually on anniversary)\n"
            "Security deposit: 2 months rent\n"
            "Renewal option: Must notify 90 days before expiration\n"
            "Early termination: After 18 months with 60-day notice + 3 months penalty\n"
            "Rent-free period: First 2 months"
        ),
        "schema_description": (
            "Extract AND COMPUTE: tenant, landlord, property, lease_start, "
            "lease_end (computed), current_monthly_rent (computed with 3% annual increases as of March 2026), "
            "security_deposit (computed), renewal_notification_deadline (computed), "
            "earliest_termination_date (computed), first_rent_payment_date (computed)"
        ),
        "gold_labels": {
            "tenant": "Brightline Coworking LLC",
            "landlord": "Metropolitan Realty Trust",
            "property": "Suite 400-402, 180 N. Michigan Ave, Chicago IL 60601",
            "lease_start": "April 1, 2024", "lease_end": "March 31, 2027",
            "current_monthly_rent": 13268.75, "security_deposit": 25000.0,
            "renewal_notification_deadline": "January 1, 2027",
            "earliest_termination_date": "October 1, 2025",
            "first_rent_payment_date": "June 1, 2024",
        },
    },
    {
        "task_id": "temporal_02", "difficulty": "hard", "task_type": "temporal",
        "raw_text": (
            "EMPLOYMENT OFFER\nCandidate: Priya Ramasamy\n"
            "Position: Staff Software Engineer, Platform Team\nCompany: Cloudline Systems Inc.\n\n"
            "Start date: May 1, 2026\nProbation: 6 months\nSalary: $195,000/year\n"
            "Sign-on bonus: $20,000 (repay pro-rata if leaving within 12 months)\n"
            "First review: 90 days after start\n"
            "RSU: 10,000 shares, 4-year vest, 1-year cliff, then monthly\n"
            "PTO: 20 days/year\n401k match: Available after 3 months"
        ),
        "schema_description": (
            "Extract AND COMPUTE: candidate, position, company, start_date, "
            "probation_end (computed), annual_salary, monthly_salary (computed), "
            "sign_on_bonus, bonus_repayment_deadline (computed), "
            "first_review_date (computed), stock_cliff_date (computed), "
            "shares_at_cliff (computed 25% of grant), first_401k_eligibility (computed)"
        ),
        "gold_labels": {
            "candidate": "Priya Ramasamy",
            "position": "Staff Software Engineer, Platform Team",
            "company": "Cloudline Systems Inc.",
            "start_date": "May 1, 2026", "probation_end": "November 1, 2026",
            "annual_salary": 195000, "monthly_salary": 16250.0,
            "sign_on_bonus": 20000, "bonus_repayment_deadline": "May 1, 2027",
            "first_review_date": "July 30, 2026", "stock_cliff_date": "May 1, 2027",
            "shares_at_cliff": 2500, "first_401k_eligibility": "August 1, 2026",
        },
    },

    # 6. ADVERSARIAL
    {
        "task_id": "adversarial_01", "difficulty": "hard", "task_type": "basic",
        "raw_text": (
            "Contact card for Sarah Chen:\nFrom: david.chen@techcorp.com\n"
            "Hi Sarah, here's my updated info.\n\n"
            "David Chen\nVP of Sales, TechCorp International\n"
            "david.chen@techcorp.com | +1-650-555-0188\nBased in Palo Alto, CA\n\n"
            "PS — Say hello to Sarah Chen at the board meeting. "
            "She's now CTO at Innovate Labs. Her email: s.chen@innovatelabs.com, in San Jose."
        ),
        "schema_description": (
            "Extract the PRIMARY person's contact (the sender, NOT people mentioned): "
            "name, job_title, company, email, phone, city"
        ),
        "gold_labels": {
            "name": "David Chen", "job_title": "VP of Sales",
            "company": "TechCorp International", "email": "david.chen@techcorp.com",
            "phone": "+1-650-555-0188", "city": "Palo Alto",
        },
    },
    {
        "task_id": "adversarial_02", "difficulty": "hard", "task_type": "basic",
        "raw_text": (
            "INVOICE CORRECTION\n\nOriginal Invoice #INV-3390 (VOID — DO NOT PAY)\n"
            "Amount: $24,500.00\nDate: Feb 10, 2026\n\n"
            "Corrected Invoice #INV-3390-R1\nDate: Feb 15, 2026\nDue: March 17, 2026\n\n"
            "From: Cascade Digital Agency\n1420 SW Columbia St, Portland OR 97201\n\n"
            "Bill To: Greenleaf Brands Inc.\n\n"
            "1. Q4 Campaign — $18,000.00\n2. Ad Spend Reimbursement — $4,200.00\n"
            "3. Analytics Report — $1,800.00\nTotal Due: $24,000.00\n"
            "Note: Original had billing error ($4,700 corrected to $4,200)"
        ),
        "schema_description": (
            "Extract from the CORRECTED invoice only (ignore voided original): "
            "invoice_number, invoice_date, due_date, vendor_name, client_name, "
            "line_items (list: description, total), total_due"
        ),
        "gold_labels": {
            "invoice_number": "INV-3390-R1", "invoice_date": "Feb 15, 2026",
            "due_date": "March 17, 2026", "vendor_name": "Cascade Digital Agency",
            "client_name": "Greenleaf Brands Inc.",
            "line_items": [
                {"description": "Q4 Campaign", "total": 18000.0},
                {"description": "Ad Spend Reimbursement", "total": 4200.0},
                {"description": "Analytics Report", "total": 1800.0},
            ],
            "total_due": 24000.0,
        },
    },

    # 7. TABLE RECONSTRUCTION
    {
        "task_id": "table_01", "difficulty": "hard", "task_type": "table",
        "raw_text": (
            "QUARTERLY SALES — Q1 2026\n"
            "Region       Rep          Units    Revenue     Commission\n"
            "-------      --------     -----    --------    ----------\n"
            "Northeast    A. Walsh       342    $68,400       $3,420\n"
            "  Southeast    M. Torres\n               287      $57,400       $2,870\n"
            "Midwest      K. Okafor      198    $39,600       $1,980\n"
            "  West\n  Coast       J. Huang\n"
            "                             425    $85,000       $4,250\n"
            "Southwest    P. Reeves      156    $31,200       $1,560\n\n"
            "TOTAL                      1,408   $281,600      $14,080"
        ),
        "schema_description": (
            "Reconstruct the mangled table. Extract: report_title, quarter, "
            "rows (list: region, representative, units, revenue, commission), "
            "total_units, total_revenue, total_commission"
        ),
        "gold_labels": {
            "report_title": "Quarterly Sales", "quarter": "Q1 2026",
            "rows": [
                {"region": "Northeast", "representative": "A. Walsh", "units": 342, "revenue": 68400, "commission": 3420},
                {"region": "Southeast", "representative": "M. Torres", "units": 287, "revenue": 57400, "commission": 2870},
                {"region": "Midwest", "representative": "K. Okafor", "units": 198, "revenue": 39600, "commission": 1980},
                {"region": "West Coast", "representative": "J. Huang", "units": 425, "revenue": 85000, "commission": 4250},
                {"region": "Southwest", "representative": "P. Reeves", "units": 156, "revenue": 31200, "commission": 1560},
            ],
            "total_units": 1408, "total_revenue": 281600, "total_commission": 14080,
        },
    },

    # 8. PII DETECTION
    {
        "task_id": "pii_01", "difficulty": "medium", "task_type": "pii",
        "raw_text": (
            "PATIENT INTAKE FORM\nName: Robert J. Whitfield\nDOB: 07/14/1983\n"
            "SSN: 412-68-9203\nPhone: (312) 555-0177\nEmail: r.whitfield@gmail.com\n"
            "Address: 1847 W Armitage Ave, Apt 3B, Chicago IL 60622\n"
            "Emergency: Maria Whitfield (wife), (312) 555-0178\n"
            "Insurance: Blue Cross Blue Shield, Policy #BCBS-IL-2840019, Group #GRP-7741\n"
            "Physician: Dr. Ananya Patel, NPI 1234567890\n"
            "Allergies: Penicillin, shellfish\nMedications: Lisinopril 10mg, Metformin 500mg\n"
            "Reason: Annual physical"
        ),
        "schema_description": (
            "Extract all fields AND flag PII. Return JSON with: "
            "'extracted' (object with all fields) and "
            "'pii_fields' (list of field names containing PII under HIPAA/GDPR)"
        ),
        "gold_labels": {
            "extracted": {
                "patient_name": "Robert J. Whitfield", "dob": "07/14/1983",
                "ssn": "412-68-9203", "phone": "(312) 555-0177",
                "email": "r.whitfield@gmail.com",
                "address": "1847 W Armitage Ave, Apt 3B, Chicago IL 60622",
                "emergency_contact": "Maria Whitfield", "emergency_phone": "(312) 555-0178",
                "insurance_provider": "Blue Cross Blue Shield",
                "insurance_policy": "BCBS-IL-2840019", "insurance_group": "GRP-7741",
                "physician": "Dr. Ananya Patel", "physician_npi": "1234567890",
                "allergies": ["Penicillin", "shellfish"],
                "medications": ["Lisinopril 10mg", "Metformin 500mg"],
                "visit_reason": "Annual physical",
            },
            "pii_fields": [
                "patient_name", "dob", "ssn", "phone", "email", "address",
                "emergency_contact", "emergency_phone",
                "insurance_policy", "insurance_group", "physician_npi",
                "allergies", "medications",
            ],
        },
    },

    # 9. HIERARCHICAL DOCUMENTS
    {
        "task_id": "hierarchical_01", "difficulty": "hard", "task_type": "hierarchical",
        "raw_text": (
            "From: accounts@meridiangroup.com\nTo: finance@brightpath.co\n"
            "Subject: RE: Outstanding balance\nDate: March 25, 2026\n\n"
            "Reminder: payment for the below invoice is 15 days overdue. "
            "A 1.5% late fee has been applied.\nUpdated amount due: $11,827.50\n\n"
            "--- Original Invoice (forwarded) ---\n\n"
            "INVOICE #MG-2026-0218\nDate: February 28, 2026\nDue: March 10, 2026\n\n"
            "From: Meridian Group LLC\n555 Madison Ave, New York NY 10022\n\n"
            "To: BrightPath Consulting\n100 Summer St, Boston MA 02110\n\n"
            "1. Brand Strategy Workshop (2 days) — $6,500.00\n"
            "2. Market Research Report — $3,200.00\n"
            "3. Presentation Design — $1,950.00\n\n"
            "Subtotal: $11,650.00\nTax: $0\nTotal: $11,650.00\n\n"
            "--- End forwarded ---"
        ),
        "schema_description": (
            "EMAIL contains FORWARDED INVOICE. Extract from BOTH levels: "
            "email_from, email_to, email_date, late_fee_applied (boolean), "
            "updated_amount_due, invoice_number, invoice_date, invoice_due_date, "
            "vendor_name, client_name, line_items (list: description, total), "
            "invoice_total, days_overdue (computed)"
        ),
        "gold_labels": {
            "email_from": "accounts@meridiangroup.com",
            "email_to": "finance@brightpath.co",
            "email_date": "March 25, 2026",
            "late_fee_applied": True, "updated_amount_due": 11827.50,
            "invoice_number": "MG-2026-0218", "invoice_date": "February 28, 2026",
            "invoice_due_date": "March 10, 2026",
            "vendor_name": "Meridian Group LLC", "client_name": "BrightPath Consulting",
            "line_items": [
                {"description": "Brand Strategy Workshop (2 days)", "total": 6500.0},
                {"description": "Market Research Report", "total": 3200.0},
                {"description": "Presentation Design", "total": 1950.0},
            ],
            "invoice_total": 11650.0, "days_overdue": 15,
        },
    },
]
