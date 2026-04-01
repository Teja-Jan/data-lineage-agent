# Enterprise Data Lineage and Impact Intelligent Analysis

[Open In Colab](https://colab.research.google.com/github/Teja-Jan/data-lineage-agent/blob/master/enterprise-lineage-colab.ipynb)

An advanced, AI-driven data intelligence platform built to dynamically analyze end-to-end data lineage, track historical changes, and determine enterprise risk impact across complex data ecosystems.

## Platform Authentication (Demo Mode)
To unlock the enterprise domain schemas within the dashboard, you must establish an initial secure connection to the UI gateway. Since the environment spins up with `ENTERPRISE_MODE=DEMO`, it is programmed to accept mock validation parameters for seamless presentation routing.

### Authorized Demo Credentials
When utilizing the **Manual Connection Entry** form on the right-hand panel, use the following placeholder details to reliably authorize the active session:
*   **Connection Type**: RDBMS (PostgreSQL/SQL Server)
*   **Hostname**: `demo-db.enterprise.io` (or any string, must not be blank)
*   **Username**: `demo_admin` (or any string, must not be blank)
*   **Password / Secret**: `********`

Click **Authenticate Connection**. The internal gatekeeper will securely register the context, unlock the user interface, and enable the drop-down to transition between the active enterprise schemas.

---

## Architecture & Active Data Connections

This application utilizes a decentralized, multi-domain metadata repository approach to manage lineage intelligence across distinct corporate environments. 

### Pre-configured Enterprise Data Domains
The agent organically routes intelligence queries by isolating active data sets. The following target architectures are currently instantiated and ready for analytical traversal. 

*Note: Even though these data sources are pre-configured locally, they strictly mandate authentication. Data lineage and intelligence can only be viewed after authenticating through the Manual Connection Entry or via Google Secret Manager in the UI.*

*   **Finance Integration (`finance_test_db.sqlite`)**: Credit, Risk, Trading Systems. 
    *   Connection Details: Select "Finance" from the Enterprise Domain dropdown on the authenticated landing page after establishing a secure RDBMS connection.
*   **Healthcare Integration (`healthcare_db.sqlite`)**: EMR, Patient Telemetry, Clinical Operations.
    *   Connection Details: Select "Healthcare" from the Enterprise Domain dropdown after authentication.
*   **Automotive Integration (`automotive_db.sqlite`)**: Manufacturing Pipelines, Telematics.
    *   Connection Details: Select "Automotive" from the Enterprise Domain dropdown after authentication.
*   **Supply Chain Integration (`supplychain_db.sqlite`)**: Procurement, Logistics, Fleet.
    *   Connection Details: Select "Supply Chain" from the Enterprise Domain dropdown after authentication.
*   **Generic Organizational Root (`org_test_db.sqlite`)**: Cross-domain HR, General Reporting.
    *   Connection Details: Select "Cross-Org/Demo" from the Enterprise Domain dropdown after authentication.

### Updating Pre-Existing Connections
To transition the system to connect to a new pre-configured data domain:
1.  Launch the user interface and complete the Authentication form (or use Google Secret Manager Fetch).
2.  Navigate to the "Select Enterprise Domain" drop-down located below the chat interface.
3.  Select the desired industry domain.
4.  The system will dynamically switch the active `sqlite` target in the background and instantly parse the new logical models, source-to-target mapping, and BI analytics metadata.

For entirely new generic external connections, utilize the Connection Entry form to connect to active PostgreSQL or SQL Server target environments.

---

## Governance Notification Configuration

The platform contains an integrated notification engine capable of delivering precise risk impact `.xlsx` analysis files directly to your Enterprise Data Governance Team. 

This engine is natively decoupled and strictly configuration-driven, meaning your deployment engineers can dynamically swap the transport mechanism without ever altering the Python codebase.

### Switching Between SendGrid (API) and SMTP
All configuration takes place within the hidden `.env` file at the root of the project.

1.  Open `.env`.
2.  Locate the `# REAL-TIME EMAIL CONFIGURATION` section.
3.  Set the `EMAIL_PROVIDER=SENDGRID` or `SMTP`.

**Example `.env` (SendGrid Mode)**:
```env
# Set EMAIL_PROVIDER to either 'SENDGRID' or 'SMTP'
EMAIL_PROVIDER=SENDGRID
GOVERNANCE_RECIPIENT=governance.team@yourdomain.com

# --- SENDGRID CONFIGURATION ---
SENDGRID_API_KEY="SG.your_long_api_key_here"
SENDGRID_FROM_EMAIL="alerts@yourdomain.com"
```

**Example `.env` (SMTP Mode)**:
If your internal intranet strictly mandates an internal SMTP relay to bypass firewalls:
```env
EMAIL_PROVIDER=SMTP
GOVERNANCE_RECIPIENT=governance.team@yourdomain.com

# --- SMTP CONFIGURATION ---
SMTP_SERVER=mail.internalcorp.local
SMTP_PORT=1025
SMTP_USER="service_account"
SMTP_PASSWORD="secure_password"
```

Once the `.env` file is saved, any click of the "Notify Governance Team" button inside the analytical interface will immediately obey the new routing protocol.

---

## Execution & Deployment

### Local Deployment
```bash
# 1. Install standard dependencies
pip install -r requirements.txt

# 2. Launch Streamlit Engine
python -m streamlit run src/app.py 
```

### Google Colab Sandbox
To spin up a fully isolated, externalized web demo from Github:
1. Click the [Open In Colab] link at the top of this documentation.
2. Ensure you have populated your SendGrid API credentials inside the `.env` creation block in the notebook.
3. Choose "Run All".
4. Colab will generate a public `loca.lt` tunnel allowing access to the web interface from anywhere.
