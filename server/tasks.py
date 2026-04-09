"""Task bank for Structured Data Extraction environment."""

TASKS = [
    # ── EASY: Contact card extraction ──
    {
        "task_id": "contact_01",
        "difficulty": "easy",
        "task_type": "basic",
        "raw_text": (
            "Hey! Just met Sarah Chen at the ML meetup. She works as a Senior Data Scientist "
            "at Meridian Analytics. Her email is s.chen@meridian-analytics.com and she said "
            "to call her at +1-415-829-3374 if we want to discuss the collab. She's based in "
            "San Francisco."
        ),
        "schema_description": (
            "Extract: name (string), job_title (string), company (string), "
            "email (string), phone (string), city (string)"
        ),
        "gold_labels": {
            "name": "Sarah Chen",
            "job_title": "Senior Data Scientist",
            "company": "Meridian Analytics",
            "email": "s.chen@meridian-analytics.com",
            "phone": "+1-415-829-3374",
            "city": "San Francisco",
        },
    },
    {
        "task_id": "contact_02",
        "difficulty": "easy",
        "raw_text": (
            "FYI — Raj Patel from CloudBridge Solutions (raj.patel@cloudbridge.io) pinged me "
            "on LinkedIn. He's their VP of Engineering, based out of Austin TX. Mobile: "
            "(512) 555-0198. Wants to chat about our API integration."
        ),
        "schema_description": (
            "Extract: name (string), job_title (string), company (string), "
            "email (string), phone (string), city (string)"
        ),
        "gold_labels": {
            "name": "Raj Patel",
            "job_title": "VP of Engineering",
            "company": "CloudBridge Solutions",
            "email": "raj.patel@cloudbridge.io",
            "phone": "(512) 555-0198",
            "city": "Austin",
        },
    },
    {
        "task_id": "contact_03",
        "difficulty": "easy",
        "raw_text": (
            "Business card scan: Dr. Emily Rodriguez | Chief Medical Officer | NovaCare Health "
            "Systems | emily.rodriguez@novacare.org | Direct: 212-443-8821 | New York, NY 10001"
        ),
        "schema_description": (
            "Extract: name (string), job_title (string), company (string), "
            "email (string), phone (string), city (string)"
        ),
        "gold_labels": {
            "name": "Dr. Emily Rodriguez",
            "job_title": "Chief Medical Officer",
            "company": "NovaCare Health Systems",
            "email": "emily.rodriguez@novacare.org",
            "phone": "212-443-8821",
            "city": "New York",
        },
    },
    # ── MEDIUM: Job posting extraction ──
    {
        "task_id": "job_01",
        "difficulty": "medium",
        "raw_text": (
            "We're hiring! Acme Robotics is looking for a Machine Learning Engineer to join "
            "our Perception team in Pittsburgh, PA. This is a full-time role offering "
            "$140,000 - $185,000/year plus equity. Requirements: 3+ years experience with "
            "PyTorch or TensorFlow, MS in CS or related field, experience with computer vision "
            "pipelines. Nice to have: publications in top-tier venues, experience with ROS. "
            "Benefits include health/dental/vision, 401k match, unlimited PTO. "
            "Remote-friendly with 2 days/week in office. Apply by June 30, 2026."
        ),
        "schema_description": (
            "Extract: job_title (string), company (string), location (string), "
            "employment_type (string), salary_min (number), salary_max (number), "
            "salary_currency (string), required_skills (list of strings), "
            "preferred_skills (list of strings), benefits (list of strings), "
            "remote_policy (string), application_deadline (string)"
        ),
        "gold_labels": {
            "job_title": "Machine Learning Engineer",
            "company": "Acme Robotics",
            "location": "Pittsburgh, PA",
            "employment_type": "full-time",
            "salary_min": 140000,
            "salary_max": 185000,
            "salary_currency": "USD",
            "required_skills": ["PyTorch or TensorFlow", "MS in CS or related field", "computer vision pipelines"],
            "preferred_skills": ["publications in top-tier venues", "experience with ROS"],
            "benefits": ["health/dental/vision", "401k match", "unlimited PTO"],
            "remote_policy": "hybrid",
            "application_deadline": "June 30, 2026",
        },
    },
    {
        "task_id": "job_02",
        "difficulty": "medium",
        "raw_text": (
            "Position: Senior Backend Developer at FinLedger Inc. — Remote (US only). "
            "Compensation: $160K-$200K base + annual bonus up to 20%. We need someone with "
            "5+ years in Go or Rust, strong distributed systems background, and experience "
            "with PostgreSQL and Redis. Familiarity with Kubernetes and AWS is a plus. "
            "We offer stock options, parental leave (16 weeks), home office stipend ($2000), "
            "and conference budget. Start date: ASAP. Equal opportunity employer."
        ),
        "schema_description": (
            "Extract: job_title (string), company (string), location (string), "
            "employment_type (string), salary_min (number), salary_max (number), "
            "salary_currency (string), required_skills (list of strings), "
            "preferred_skills (list of strings), benefits (list of strings), "
            "remote_policy (string), application_deadline (string or null)"
        ),
        "gold_labels": {
            "job_title": "Senior Backend Developer",
            "company": "FinLedger Inc.",
            "location": "Remote (US only)",
            "employment_type": "full-time",
            "salary_min": 160000,
            "salary_max": 200000,
            "salary_currency": "USD",
            "required_skills": ["Go or Rust", "distributed systems", "PostgreSQL", "Redis"],
            "preferred_skills": ["Kubernetes", "AWS"],
            "benefits": ["stock options", "parental leave", "home office stipend", "conference budget"],
            "remote_policy": "remote",
            "application_deadline": None,
        },
    },
    {
        "task_id": "job_03",
        "difficulty": "medium",
        "raw_text": (
            "Internship Opportunity — Product Design Intern at Bloom Studios, London UK. "
            "Duration: 12 weeks (Sep-Nov 2026). Stipend: £2,500/month. Looking for current "
            "students in UX/UI design or HCI programs. Must know Figma proficiently. "
            "Bonus if you have experience with motion design or prototyping in Framer. "
            "Perks: mentorship program, portfolio review, possible full-time conversion. "
            "Apply via bloom-studios.co.uk/careers by August 1, 2026."
        ),
        "schema_description": (
            "Extract: job_title (string), company (string), location (string), "
            "employment_type (string), salary_min (number), salary_max (number), "
            "salary_currency (string), required_skills (list of strings), "
            "preferred_skills (list of strings), benefits (list of strings), "
            "remote_policy (string), application_deadline (string)"
        ),
        "gold_labels": {
            "job_title": "Product Design Intern",
            "company": "Bloom Studios",
            "location": "London, UK",
            "employment_type": "internship",
            "salary_min": 2500,
            "salary_max": 2500,
            "salary_currency": "GBP",
            "required_skills": ["UX/UI design or HCI", "Figma"],
            "preferred_skills": ["motion design", "Framer"],
            "benefits": ["mentorship program", "portfolio review", "possible full-time conversion"],
            "remote_policy": "on-site",
            "application_deadline": "August 1, 2026",
        },
    },
    # ── HARD: Invoice extraction with line items ──
    {
        "task_id": "invoice_01",
        "difficulty": "hard",
        "raw_text": (
            "INVOICE #INV-2026-04821\n"
            "Date: March 15, 2026\n"
            "Due: April 14, 2026\n\n"
            "From: Orion Digital Services LLC\n"
            "123 Innovation Drive, Suite 400, Denver CO 80202\n"
            "Tax ID: 84-2938475\n\n"
            "Bill To: Greenfield Consulting Group\n"
            "Attn: Maria Vasquez, Accounts Payable\n"
            "456 Market Street, Portland OR 97201\n\n"
            "Items:\n"
            "1. Website Redesign (Phase 2) — 80 hrs @ $150/hr = $12,000.00\n"
            "2. SEO Audit & Implementation — flat fee = $3,500.00\n"
            "3. Monthly Hosting (Jan-Mar 2026) — 3 months @ $250/mo = $750.00\n"
            "4. SSL Certificate Renewal — 1 yr = $120.00\n"
            "5. Emergency bug fixes (Feb 2026) — 6.5 hrs @ $175/hr = $1,137.50\n\n"
            "Subtotal: $17,507.50\n"
            "Tax (8.1%): $1,418.11\n"
            "Total Due: $18,925.61\n\n"
            "Payment: Wire to First National Bank, Acct 9382-0041-7756, Routing 102003154\n"
            "Terms: Net 30. Late fee of 1.5%/month on outstanding balance."
        ),
        "schema_description": (
            "Extract: invoice_number (string), invoice_date (string), due_date (string), "
            "vendor_name (string), vendor_address (string), vendor_tax_id (string), "
            "client_name (string), client_contact (string), client_address (string), "
            "line_items (list of objects with: description, quantity, unit_price, total), "
            "subtotal (number), tax_rate (number), tax_amount (number), "
            "total_due (number), payment_terms (string)"
        ),
        "gold_labels": {
            "invoice_number": "INV-2026-04821",
            "invoice_date": "March 15, 2026",
            "due_date": "April 14, 2026",
            "vendor_name": "Orion Digital Services LLC",
            "vendor_address": "123 Innovation Drive, Suite 400, Denver CO 80202",
            "vendor_tax_id": "84-2938475",
            "client_name": "Greenfield Consulting Group",
            "client_contact": "Maria Vasquez",
            "client_address": "456 Market Street, Portland OR 97201",
            "line_items": [
                {"description": "Website Redesign (Phase 2)", "quantity": 80, "unit_price": 150.0, "total": 12000.00},
                {"description": "SEO Audit & Implementation", "quantity": 1, "unit_price": 3500.0, "total": 3500.00},
                {"description": "Monthly Hosting (Jan-Mar 2026)", "quantity": 3, "unit_price": 250.0, "total": 750.00},
                {"description": "SSL Certificate Renewal", "quantity": 1, "unit_price": 120.0, "total": 120.00},
                {"description": "Emergency bug fixes (Feb 2026)", "quantity": 6.5, "unit_price": 175.0, "total": 1137.50},
            ],
            "subtotal": 17507.50,
            "tax_rate": 8.1,
            "tax_amount": 1418.11,
            "total_due": 18925.61,
            "payment_terms": "Net 30",
        },
    },
    {
        "task_id": "invoice_02",
        "difficulty": "hard",
        "raw_text": (
            "CREDIT NOTE #CN-7743\n"
            "Issued: 2026-02-28\n"
            "Reference Invoice: INV-2025-11092\n\n"
            "Supplier: Kato Industrial Supply Co.\n"
            "8-22 Nihonbashi, Chuo-ku, Tokyo 103-0027 Japan\n"
            "VAT: JP-T4010001012345\n\n"
            "Customer: EuroParts GmbH\n"
            "Contact: Klaus Fischer, Procurement\n"
            "Industriestr. 45, 70565 Stuttgart, Germany\n\n"
            "Credited Items:\n"
            "A) Titanium Fastener Set TFS-200 — returned 50 units @ ¥1,200 ea = ¥60,000\n"
            "B) Hydraulic Seal Kit HSK-45 — defective batch, 20 units @ ¥3,400 ea = ¥68,000\n"
            "C) Shipping refund for original order = ¥8,500\n\n"
            "Credit Subtotal: ¥136,500\n"
            "Consumption Tax (10%): ¥13,650\n"
            "Total Credit: ¥150,150\n\n"
            "Credit will be applied to next purchase order. Valid for 12 months from issue date."
        ),
        "schema_description": (
            "Extract: invoice_number (string), invoice_date (string), due_date (string or null), "
            "vendor_name (string), vendor_address (string), vendor_tax_id (string), "
            "client_name (string), client_contact (string), client_address (string), "
            "line_items (list of objects with: description, quantity, unit_price, total), "
            "subtotal (number), tax_rate (number), tax_amount (number), "
            "total_due (number), payment_terms (string)"
        ),
        "gold_labels": {
            "invoice_number": "CN-7743",
            "invoice_date": "2026-02-28",
            "due_date": None,
            "vendor_name": "Kato Industrial Supply Co.",
            "vendor_address": "8-22 Nihonbashi, Chuo-ku, Tokyo 103-0027 Japan",
            "vendor_tax_id": "JP-T4010001012345",
            "client_name": "EuroParts GmbH",
            "client_contact": "Klaus Fischer",
            "client_address": "Industriestr. 45, 70565 Stuttgart, Germany",
            "line_items": [
                {"description": "Titanium Fastener Set TFS-200", "quantity": 50, "unit_price": 1200, "total": 60000},
                {"description": "Hydraulic Seal Kit HSK-45", "quantity": 20, "unit_price": 3400, "total": 68000},
                {"description": "Shipping refund for original order", "quantity": 1, "unit_price": 8500, "total": 8500},
            ],
            "subtotal": 136500,
            "tax_rate": 10.0,
            "tax_amount": 13650,
            "total_due": 150150,
            "payment_terms": "Credit applied to next purchase order, valid 12 months",
        },
    },
    {
        "task_id": "invoice_03",
        "difficulty": "hard",
        "raw_text": (
            "Invoice: TF/2026/0339\n"
            "Date of issue: 1 April 2026\n"
            "Payment due by: 1 May 2026\n\n"
            "Thornfield & Associates LLP\n"
            "14 Chancery Lane, London WC2A 1PL\n"
            "VAT Reg: GB 293 8475 12\n\n"
            "Billed to: Crestwood Properties Ltd\n"
            "For the attention of: James Whitmore, Finance Director\n"
            "90 Victoria Embankment, London EC4Y 0DH\n\n"
            "Professional services rendered:\n"
            "  (i)   Commercial lease review & negotiation — 22 hrs @ £350/hr — £7,700.00\n"
            "  (ii)  Planning permission application — fixed fee — £4,200.00\n"
            "  (iii) Title search & due diligence — 15 hrs @ £300/hr — £4,500.00\n"
            "  (iv)  Stamp duty advisory — 5 hrs @ £400/hr — £2,000.00\n"
            "  (v)   Disbursements (Land Registry fees, courier) — £385.00\n\n"
            "Net total: £18,785.00\n"
            "VAT @ 20%: £3,757.00\n"
            "Amount payable: £22,542.00\n\n"
            "Bank: Barclays, Sort 20-45-67, Acct 83920146. Quote ref TF/2026/0339.\n"
            "Terms: Payment within 30 days. Interest charged at 4% above BoE base rate on "
            "overdue amounts per Late Payment of Commercial Debts Act 1998."
        ),
        "schema_description": (
            "Extract: invoice_number (string), invoice_date (string), due_date (string), "
            "vendor_name (string), vendor_address (string), vendor_tax_id (string), "
            "client_name (string), client_contact (string), client_address (string), "
            "line_items (list of objects with: description, quantity, unit_price, total), "
            "subtotal (number), tax_rate (number), tax_amount (number), "
            "total_due (number), payment_terms (string)"
        ),
        "gold_labels": {
            "invoice_number": "TF/2026/0339",
            "invoice_date": "1 April 2026",
            "due_date": "1 May 2026",
            "vendor_name": "Thornfield & Associates LLP",
            "vendor_address": "14 Chancery Lane, London WC2A 1PL",
            "vendor_tax_id": "GB 293 8475 12",
            "client_name": "Crestwood Properties Ltd",
            "client_contact": "James Whitmore",
            "client_address": "90 Victoria Embankment, London EC4Y 0DH",
            "line_items": [
                {"description": "Commercial lease review & negotiation", "quantity": 22, "unit_price": 350.0, "total": 7700.00},
                {"description": "Planning permission application", "quantity": 1, "unit_price": 4200.0, "total": 4200.00},
                {"description": "Title search & due diligence", "quantity": 15, "unit_price": 300.0, "total": 4500.00},
                {"description": "Stamp duty advisory", "quantity": 5, "unit_price": 400.0, "total": 2000.00},
                {"description": "Disbursements (Land Registry fees, courier)", "quantity": 1, "unit_price": 385.0, "total": 385.00},
            ],
            "subtotal": 18785.00,
            "tax_rate": 20.0,
            "tax_amount": 3757.00,
            "total_due": 22542.00,
            "payment_terms": "Payment within 30 days",
        },
    },
    # ── EASY: Support ticket extraction ──
    {
        "task_id": "contact_04",
        "difficulty": "easy",
        "raw_text": (
            "Ticket from: Mike O'Brien, CTO @ TrueStack (mike@truestack.dev). "
            "Submitted via chat at 3:42 PM. Phone for callback: 650-321-9987. "
            "He's in Seattle. Issue: dashboard loading times exceed 10s after latest deploy."
        ),
        "schema_description": (
            "Extract: name (string), job_title (string), company (string), "
            "email (string), phone (string), city (string)"
        ),
        "gold_labels": {
            "name": "Mike O'Brien",
            "job_title": "CTO",
            "company": "TrueStack",
            "email": "mike@truestack.dev",
            "phone": "650-321-9987",
            "city": "Seattle",
        },
    },
    # ── MEDIUM: Product listing extraction ──
    {
        "task_id": "job_04",
        "difficulty": "medium",
        "raw_text": (
            "NOW HIRING — DevOps Lead at Quantum Mesh, Toronto ON (hybrid, 3 days on-site). "
            "CAD $130,000–$165,000 + 15% performance bonus. Must have: 7+ years in cloud infra, "
            "expert-level Terraform and Kubernetes, CI/CD pipeline design (GitHub Actions or "
            "GitLab CI), strong Linux administration. Nice to have: HashiCorp Vault, service "
            "mesh experience (Istio/Linkerd), SOC 2 compliance knowledge. We provide extended "
            "health coverage, $5K annual learning budget, and 4 weeks vacation. Applications "
            "close July 15, 2026."
        ),
        "schema_description": (
            "Extract: job_title (string), company (string), location (string), "
            "employment_type (string), salary_min (number), salary_max (number), "
            "salary_currency (string), required_skills (list of strings), "
            "preferred_skills (list of strings), benefits (list of strings), "
            "remote_policy (string), application_deadline (string)"
        ),
        "gold_labels": {
            "job_title": "DevOps Lead",
            "company": "Quantum Mesh",
            "location": "Toronto, ON",
            "employment_type": "full-time",
            "salary_min": 130000,
            "salary_max": 165000,
            "salary_currency": "CAD",
            "required_skills": [
                "cloud infrastructure",
                "Terraform",
                "Kubernetes",
                "CI/CD pipeline design",
                "Linux administration",
            ],
            "preferred_skills": [
                "HashiCorp Vault",
                "service mesh (Istio/Linkerd)",
                "SOC 2 compliance",
            ],
            "benefits": [
                "extended health coverage",
                "learning budget",
                "4 weeks vacation",
            ],
            "remote_policy": "hybrid",
            "application_deadline": "July 15, 2026",
        },
    },
    # ── HARD: Medical report extraction ──
    {
        "task_id": "invoice_04",
        "difficulty": "hard",
        "raw_text": (
            "PURCHASE ORDER #PO-2026-5581\n"
            "Date: 20 March 2026\n"
            "Delivery required by: 10 April 2026\n\n"
            "Buyer: Apex Manufacturing Corp.\n"
            "700 Industrial Blvd, Unit 12, Detroit MI 48201\n"
            "EIN: 38-4829175\n\n"
            "Supplier: Global Raw Materials AG\n"
            "Contact: Luisa Fernandez, Sales Director\n"
            "Bahnhofstrasse 22, 8001 Zurich, Switzerland\n\n"
            "Order Lines:\n"
            "  L1. Cold-rolled steel sheet CR-304 (2mm) — 500 kg @ $4.20/kg — $2,100.00\n"
            "  L2. Aluminum extrusion AL-6063-T5 — 200 units @ $18.50/unit — $3,700.00\n"
            "  L3. Nylon spacer kit NSK-12 — 1,000 pcs @ $0.85/pc — $850.00\n"
            "  L4. Stainless hex bolts M8x40 (A2-70) — 5,000 pcs @ $0.12/pc — $600.00\n"
            "  L5. Freight & handling (DDP Detroit) — lump sum — $1,450.00\n"
            "  L6. Customs brokerage fee — flat — $375.00\n\n"
            "Subtotal: $9,075.00\n"
            "Sales Tax (6%): $544.50\n"
            "Grand Total: $9,619.50\n\n"
            "Payment: 50% deposit on PO acceptance, 50% on delivery. "
            "Wire to UBS AG, IBAN CH93 0076 2011 6238 5295 7, SWIFT UBSWCHZH80A."
        ),
        "schema_description": (
            "Extract: invoice_number (string), invoice_date (string), due_date (string), "
            "vendor_name (string), vendor_address (string), vendor_tax_id (string), "
            "client_name (string), client_contact (string), client_address (string), "
            "line_items (list of objects with: description, quantity, unit_price, total), "
            "subtotal (number), tax_rate (number), tax_amount (number), "
            "total_due (number), payment_terms (string)"
        ),
        "gold_labels": {
            "invoice_number": "PO-2026-5581",
            "invoice_date": "20 March 2026",
            "due_date": "10 April 2026",
            "vendor_name": "Global Raw Materials AG",
            "vendor_address": "Bahnhofstrasse 22, 8001 Zurich, Switzerland",
            "vendor_tax_id": "38-4829175",
            "client_name": "Apex Manufacturing Corp.",
            "client_contact": "Luisa Fernandez",
            "client_address": "700 Industrial Blvd, Unit 12, Detroit MI 48201",
            "line_items": [
                {"description": "Cold-rolled steel sheet CR-304 (2mm)", "quantity": 500, "unit_price": 4.20, "total": 2100.00},
                {"description": "Aluminum extrusion AL-6063-T5", "quantity": 200, "unit_price": 18.50, "total": 3700.00},
                {"description": "Nylon spacer kit NSK-12", "quantity": 1000, "unit_price": 0.85, "total": 850.00},
                {"description": "Stainless hex bolts M8x40 (A2-70)", "quantity": 5000, "unit_price": 0.12, "total": 600.00},
                {"description": "Freight & handling (DDP Detroit)", "quantity": 1, "unit_price": 1450.00, "total": 1450.00},
                {"description": "Customs brokerage fee", "quantity": 1, "unit_price": 375.00, "total": 375.00},
            ],
            "subtotal": 9075.00,
            "tax_rate": 6.0,
            "tax_amount": 544.50,
            "total_due": 9619.50,
            "payment_terms": "50% deposit on PO acceptance, 50% on delivery",
        },
    },
    # ── EASY: Support ticket extraction ──
    {
        "task_id": "ticket_01",
        "difficulty": "easy",
        "raw_text": (
            "Ticket #TK-29481 | Priority: High | Created: 2026-03-12 09:14 UTC\n"
            "Customer: Amanda Liu (amanda.liu@fastmail.com) — Pro Plan\n"
            "Subject: Cannot export CSV reports since yesterday\n\n"
            "Hi support team, since yesterday afternoon I've been getting a 500 error "
            "every time I try to export my monthly sales report as CSV. I've tried Chrome "
            "and Firefox, cleared cache, same issue. This is blocking my end-of-quarter "
            "reporting. My account ID is ACC-8827. I need this resolved ASAP. Thanks, Amanda"
        ),
        "schema_description": (
            "Extract: ticket_id (string), priority (string), created_at (string), "
            "customer_name (string), customer_email (string), plan_type (string), "
            "subject (string), issue_category (string: bug/feature/billing/access), "
            "affected_feature (string), account_id (string)"
        ),
        "gold_labels": {
            "ticket_id": "TK-29481",
            "priority": "High",
            "created_at": "2026-03-12 09:14 UTC",
            "customer_name": "Amanda Liu",
            "customer_email": "amanda.liu@fastmail.com",
            "plan_type": "Pro",
            "subject": "Cannot export CSV reports since yesterday",
            "issue_category": "bug",
            "affected_feature": "CSV export",
            "account_id": "ACC-8827",
        },
    },
    {
        "task_id": "ticket_02",
        "difficulty": "easy",
        "raw_text": (
            "Ticket #TK-30102 | Priority: Medium | Created: 2026-03-18 14:22 UTC\n"
            "Customer: Carlos Mendoza (carlos.m@outlook.com) — Free Plan\n"
            "Subject: Request to upgrade and add team members\n\n"
            "Hello, I'm currently on the free plan and I'd like to upgrade to the Business "
            "plan. I also need to add 5 team members. Can you walk me through the process? "
            "Also, is there a discount for annual billing? My organization is MendozaTech, "
            "account ACC-5543. Best, Carlos"
        ),
        "schema_description": (
            "Extract: ticket_id (string), priority (string), created_at (string), "
            "customer_name (string), customer_email (string), plan_type (string), "
            "subject (string), issue_category (string: bug/feature/billing/access), "
            "affected_feature (string), account_id (string)"
        ),
        "gold_labels": {
            "ticket_id": "TK-30102",
            "priority": "Medium",
            "created_at": "2026-03-18 14:22 UTC",
            "customer_name": "Carlos Mendoza",
            "customer_email": "carlos.m@outlook.com",
            "plan_type": "Free",
            "subject": "Request to upgrade and add team members",
            "issue_category": "billing",
            "affected_feature": "plan upgrade",
            "account_id": "ACC-5543",
        },
    },
    # ── MEDIUM: Receipt extraction ──
    {
        "task_id": "receipt_01",
        "difficulty": "medium",
        "raw_text": (
            "RECEIPT\n"
            "The Copper Kettle Cafe\n"
            "782 Riverside Ave, Cambridge MA 02139\n"
            "Tel: (617) 555-0234\n\n"
            "Server: Priya | Table: 7 | Date: 03/22/2026 12:47 PM\n\n"
            "2x Avocado Toast              $14.00\n"
            "1x Smoked Salmon Bagel         $9.50\n"
            "3x Flat White                  $16.50\n"
            "1x Matcha Latte                 $6.00\n"
            "1x Blueberry Muffin             $4.25\n\n"
            "Subtotal:                      $50.25\n"
            "Tax (6.25%):                    $3.14\n"
            "Tip:                            $9.00\n"
            "TOTAL:                         $62.39\n\n"
            "Paid: Visa ending 4821\n"
            "Auth: 884729\n"
            "Thank you for visiting!"
        ),
        "schema_description": (
            "Extract: store_name (string), store_address (string), store_phone (string), "
            "date (string), server_name (string), "
            "line_items (list of objects with: item_name, quantity, total), "
            "subtotal (number), tax_rate (number), tax_amount (number), "
            "tip (number), total (number), payment_method (string)"
        ),
        "gold_labels": {
            "store_name": "The Copper Kettle Cafe",
            "store_address": "782 Riverside Ave, Cambridge MA 02139",
            "store_phone": "(617) 555-0234",
            "date": "03/22/2026",
            "server_name": "Priya",
            "line_items": [
                {"item_name": "Avocado Toast", "quantity": 2, "total": 14.00},
                {"item_name": "Smoked Salmon Bagel", "quantity": 1, "total": 9.50},
                {"item_name": "Flat White", "quantity": 3, "total": 16.50},
                {"item_name": "Matcha Latte", "quantity": 1, "total": 6.00},
                {"item_name": "Blueberry Muffin", "quantity": 1, "total": 4.25},
            ],
            "subtotal": 50.25,
            "tax_rate": 6.25,
            "tax_amount": 3.14,
            "tip": 9.00,
            "total": 62.39,
            "payment_method": "Visa ending 4821",
        },
    },
    {
        "task_id": "receipt_02",
        "difficulty": "medium",
        "raw_text": (
            "URBAN HARDWARE & GARDEN\n"
            "1205 NE Alberta St, Portland OR 97211\n"
            "(503) 555-8190 | urbanhardware.com\n\n"
            "Date: 2026-04-01 15:33 | Register: 3 | Cashier: Tom B.\n\n"
            "DeWalt 20V Drill Kit          $149.99\n"
            "3/8\" Socket Set (42pc)          $34.99\n"
            "Gorilla Wood Glue 8oz           $7.49\n"
            "2x LED Shop Light 4ft          $59.98\n"
            "Ext. Cord 50ft 12ga            $42.99\n"
            "Contractor Trash Bags 50ct     $18.99\n\n"
            "Subtotal:                     $314.43\n"
            "Sales Tax (0%):                 $0.00\n"
            "TOTAL:                        $314.43\n\n"
            "Paid: Debit Mastercard ending 1190\n"
            "Returns accepted within 90 days with receipt."
        ),
        "schema_description": (
            "Extract: store_name (string), store_address (string), store_phone (string), "
            "date (string), server_name (string), "
            "line_items (list of objects with: item_name, quantity, total), "
            "subtotal (number), tax_rate (number), tax_amount (number), "
            "tip (number or null), total (number), payment_method (string)"
        ),
        "gold_labels": {
            "store_name": "Urban Hardware & Garden",
            "store_address": "1205 NE Alberta St, Portland OR 97211",
            "store_phone": "(503) 555-8190",
            "date": "2026-04-01",
            "server_name": "Tom B.",
            "line_items": [
                {"item_name": "DeWalt 20V Drill Kit", "quantity": 1, "total": 149.99},
                {"item_name": "Socket Set (42pc)", "quantity": 1, "total": 34.99},
                {"item_name": "Gorilla Wood Glue 8oz", "quantity": 1, "total": 7.49},
                {"item_name": "LED Shop Light 4ft", "quantity": 2, "total": 59.98},
                {"item_name": "Ext. Cord 50ft 12ga", "quantity": 1, "total": 42.99},
                {"item_name": "Contractor Trash Bags 50ct", "quantity": 1, "total": 18.99},
            ],
            "subtotal": 314.43,
            "tax_rate": 0.0,
            "tax_amount": 0.0,
            "tip": None,
            "total": 314.43,
            "payment_method": "Debit Mastercard ending 1190",
        },
    },
    {
        "task_id": "receipt_03",
        "difficulty": "medium",
        "raw_text": (
            "RECEIPT — Sakura Ramen House\n"
            "44 St Marks Pl, New York NY 10003\n"
            "212-555-9012\n\n"
            "Order #4418 | Dine-In | 03/28/2026 7:52 PM\n"
            "Server: Yuki\n\n"
            "1x Tonkotsu Ramen (large)      $18.00\n"
            "1x Spicy Miso Ramen            $16.00\n"
            "2x Gyoza (6pc)                 $18.00\n"
            "1x Edamame                      $5.50\n"
            "2x Asahi Draft                 $16.00\n"
            "1x Mochi Ice Cream (3pc)        $7.00\n\n"
            "Subtotal                       $80.50\n"
            "Tax (8.875%)                    $7.14\n"
            "Tip (20%)                      $16.10\n"
            "Total                         $103.74\n\n"
            "Visa *3309 — Approved\n"
            "Thank you! Please visit again."
        ),
        "schema_description": (
            "Extract: store_name (string), store_address (string), store_phone (string), "
            "date (string), server_name (string), "
            "line_items (list of objects with: item_name, quantity, total), "
            "subtotal (number), tax_rate (number), tax_amount (number), "
            "tip (number), total (number), payment_method (string)"
        ),
        "gold_labels": {
            "store_name": "Sakura Ramen House",
            "store_address": "44 St Marks Pl, New York NY 10003",
            "store_phone": "212-555-9012",
            "date": "03/28/2026",
            "server_name": "Yuki",
            "line_items": [
                {"item_name": "Tonkotsu Ramen (large)", "quantity": 1, "total": 18.00},
                {"item_name": "Spicy Miso Ramen", "quantity": 1, "total": 16.00},
                {"item_name": "Gyoza (6pc)", "quantity": 2, "total": 18.00},
                {"item_name": "Edamame", "quantity": 1, "total": 5.50},
                {"item_name": "Asahi Draft", "quantity": 2, "total": 16.00},
                {"item_name": "Mochi Ice Cream (3pc)", "quantity": 1, "total": 7.00},
            ],
            "subtotal": 80.50,
            "tax_rate": 8.875,
            "tax_amount": 7.14,
            "tip": 16.10,
            "total": 103.74,
            "payment_method": "Visa ending 3309",
        },
    },
]

# Import extended tasks (9 advanced capabilities)
try:
    from server.extended_tasks import EXTENDED_TASKS
except ImportError:
    from extended_tasks import EXTENDED_TASKS
TASKS.extend(EXTENDED_TASKS)


# Add task_type to base tasks
for _t in TASKS:
    if 'task_type' not in _t:
        _t['task_type'] = 'basic'

ALL_TASKS = TASKS
