# Adding New Domains Guide

This guide will walk you through the process of adding a new domain to the system. We'll use "Finance" as an example domain throughout this guide.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Domain Configuration](#domain-configuration)
3. [Custom Service Implementation](#custom-service-implementation)
4. [Templates and Prompts](#templates-and-prompts)
5. [Testing Your Domain](#testing-your-domain)
6. [Best Practices](#best-practices)

## Quick Start

The simplest way to add a new domain:

```bash
# 1. Create domain directory
mkdir -p domains/finance

# 2. Create config file
touch domains/finance/config.py

# 3. Add configuration (see below)

# 4. Start the service
python start_domain_service.py finance --port 8003
```

## Domain Configuration

### Basic Configuration

Create `domains/finance/config.py`:

```python
"""
Finance Domain Configuration
"""
from dataclasses import dataclass
from typing import Dict
from domains.base import BaseDomainConfig

@dataclass
class DomainConfig(BaseDomainConfig):
    """Finance domain configuration"""
    
    def __init__(self):
        super().__init__()
        self.DOMAIN_NAME = "FINANCE"
        self.DOMAIN_DOC_TYPE = "Finance"  # Used for document filtering
        
        # Custom configuration for your domain
        self.custom_config = {
            "topics": "budgeting, accounting, financial reporting, tax planning, investments",
            "systems": "QuickBooks, SAP Finance, Excel, Power BI",
            "department": "Finance Department",
            "contact": "finance@company.com"
        }
    
    def get_prompt_template(self, template_name: str) -> str:
        """Get domain-specific prompt templates"""
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, 'templates', f'{template_name}.txt')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to default template
            return self._get_default_template(template_name)
    
    def get_question_categories(self) -> Dict[int, str]:
        """Define question categories for the domain"""
        return {
            1: "Financial calculations and procedures (budgets, forecasts, reports)",
            2: "Financial policies and compliance documents",
            3: "General finance questions"
        }
    
    def _get_default_template(self, template_name: str) -> str:
        """Provide default templates if custom ones don't exist"""
        templates = {
            "system_prompt": """You are a Finance Assistant specializing in corporate finance, 
            accounting, and financial planning. Provide accurate, compliant financial guidance.""",
            
            "query_enhancement": """Enhance this finance query with relevant context:
            Query: {query}
            Enhanced Query:""",
            
            "answer_generation": """Based on the following finance documents:
            {context}
            
            Answer this question: {question}
            
            Provide a detailed, accurate response with specific references to policies and procedures."""
        }
        return templates.get(template_name, "")
```

### Advanced Configuration Options

You can add more sophisticated configuration:

```python
class DomainConfig(BaseDomainConfig):
    def __init__(self):
        super().__init__()
        self.DOMAIN_NAME = "FINANCE"
        self.DOMAIN_DOC_TYPE = "Finance"
        
        self.custom_config = {
            # Basic info
            "topics": "financial management, accounting, budgeting",
            "systems": "SAP, QuickBooks, Excel",
            
            # Advanced settings
            "enable_calculations": True,
            "currency": "USD",
            "fiscal_year_start": "January",
            "compliance_standards": ["GAAP", "SOX"],
            
            # Access control
            "restricted_topics": ["executive compensation", "M&A"],
            "public_topics": ["expense policies", "travel reimbursement"],
            
            # Integration settings
            "external_apis": {
                "exchange_rates": "https://api.exchangerate.com",
                "stock_prices": "https://api.stocks.com"
            }
        }
    
    def validate_access(self, topic: str, user_role: str) -> bool:
        """Custom access validation"""
        if topic in self.custom_config.get("restricted_topics", []):
            return user_role in ["admin", "executive"]
        return True
```

## Custom Service Implementation

For domains requiring special functionality, create a custom service:

### Create Service File

Create `services/finance/finance_service.py`:

```python
"""
Finance Service - Custom implementation for finance domain
"""
from services.common.base_service import BaseService
from typing import Dict, Any
import asyncio

class FINANCEService(BaseService):
    """Finance-specific service implementation"""
    
    def __init__(self, port: int = 8003, host: str = "0.0.0.0"):
        super().__init__(domain_name="FINANCE", port=port, host=host)
        self.logger.info("Finance Service initialized with custom features")
    
    def _add_routes(self):
        """Add finance-specific routes"""
        # First add common routes
        super()._add_routes()
        
        # Add finance-specific endpoints
        self._add_calculation_routes()
        self._add_reporting_routes()
        self._add_compliance_routes()
    
    def _add_calculation_routes(self):
        """Add financial calculation endpoints"""
        
        @self.app.post("/finance/calculate/roi")
        async def calculate_roi(investment: float, returns: float):
            """Calculate Return on Investment"""
            roi = ((returns - investment) / investment) * 100
            return {
                "investment": investment,
                "returns": returns,
                "roi_percentage": round(roi, 2),
                "interpretation": self._interpret_roi(roi)
            }
        
        @self.app.post("/finance/calculate/compound-interest")
        async def compound_interest(
            principal: float, 
            rate: float, 
            time: int, 
            frequency: int = 12
        ):
            """Calculate compound interest"""
            amount = principal * (1 + rate/100/frequency) ** (frequency * time)
            interest = amount - principal
            return {
                "principal": principal,
                "rate": rate,
                "time": time,
                "frequency": frequency,
                "total_amount": round(amount, 2),
                "interest_earned": round(interest, 2)
            }
    
    def _add_reporting_routes(self):
        """Add financial reporting endpoints"""
        
        @self.app.get("/finance/reports/summary")
        async def get_financial_summary(period: str = "current_month"):
            """Get financial summary for a period"""
            # This would connect to your financial data
            return {
                "period": period,
                "revenue": 1000000,
                "expenses": 750000,
                "profit": 250000,
                "profit_margin": 25.0,
                "key_metrics": {
                    "cash_flow": "positive",
                    "debt_ratio": 0.3,
                    "current_ratio": 1.5
                }
            }
        
        @self.app.post("/finance/reports/generate")
        async def generate_report(report_type: str, parameters: Dict[str, Any]):
            """Generate custom financial reports"""
            supported_reports = [
                "profit_loss", "balance_sheet", "cash_flow", 
                "budget_variance", "forecast"
            ]
            
            if report_type not in supported_reports:
                return {"error": f"Unsupported report type. Choose from: {supported_reports}"}
            
            # Simulate report generation
            return {
                "report_type": report_type,
                "status": "generated",
                "download_url": f"/finance/reports/download/{report_type}_20240101.pdf",
                "preview": "Report preview data..."
            }
    
    def _add_compliance_routes(self):
        """Add compliance-related endpoints"""
        
        @self.app.get("/finance/compliance/checklist")
        async def get_compliance_checklist(standard: str = "GAAP"):
            """Get compliance checklist for a standard"""
            checklists = {
                "GAAP": [
                    "Revenue recognition properly documented",
                    "Expense matching principle followed",
                    "Asset depreciation schedules updated",
                    "Financial statements reviewed"
                ],
                "SOX": [
                    "Internal controls documented",
                    "Access controls implemented",
                    "Audit trails maintained",
                    "Management certifications completed"
                ]
            }
            
            return {
                "standard": standard,
                "checklist": checklists.get(standard, []),
                "last_review": "2024-01-01",
                "next_review": "2024-04-01"
            }
    
    def _interpret_roi(self, roi: float) -> str:
        """Interpret ROI percentage"""
        if roi < 0:
            return "Negative return - Loss on investment"
        elif roi < 5:
            return "Low return - Below typical savings rate"
        elif roi < 10:
            return "Moderate return - Average performance"
        elif roi < 20:
            return "Good return - Above average performance"
        else:
            return "Excellent return - High performance investment"
```

### Create Module Init File

Create `services/finance/__init__.py`:

```python
"""Finance service module"""
from .finance_service import FINANCEService

__all__ = ['FINANCEService']
```

## Templates and Prompts

Create domain-specific templates for better responses:

### Create Templates Directory

```bash
mkdir -p domains/finance/templates
```

### System Prompt Template

Create `domains/finance/templates/system_prompt.txt`:

```
You are a Finance Assistant for {company_name}, specializing in:
- Corporate finance and accounting
- Financial planning and analysis
- Budgeting and forecasting
- Tax planning and compliance
- Investment analysis

Guidelines:
1. Always provide accurate financial information
2. Reference specific policies when applicable
3. Include relevant calculations and formulas
4. Mention compliance requirements
5. Suggest best practices for financial management

When answering:
- Be precise with numbers and calculations
- Cite relevant accounting standards (GAAP, IFRS)
- Consider tax implications
- Highlight risks and opportunities
- Provide actionable recommendations

Remember: Financial accuracy is critical. If unsure, indicate that professional consultation may be needed.
```

### Query Enhancement Template

Create `domains/finance/templates/query_enhancement.txt`:

```
Original Query: {query}

Enhanced Query for Finance Domain:
- Consider financial periods (current quarter, fiscal year, YTD)
- Include relevant financial metrics (revenue, expenses, ratios)
- Reference applicable standards (GAAP, SOX, tax codes)
- Specify department or cost center if relevant
- Include currency and geographic considerations

Enhanced Query: {enhanced_query}
```

### Answer Generation Template

Create `domains/finance/templates/answer_generation.txt`:

```
Context Documents:
{context}

Question: {question}

Provide a comprehensive financial response that includes:

1. Direct Answer: Address the specific question
2. Supporting Data: Include relevant numbers, calculations, or formulas
3. Policy References: Cite applicable policies or procedures
4. Compliance Notes: Mention any regulatory requirements
5. Best Practices: Suggest optimal approaches
6. Next Steps: Provide actionable recommendations

Format the response clearly with:
- Bullet points for key information
- Tables for numerical data
- Clear calculations with formulas
- References to source documents

Response:
```

## Testing Your Domain

### 1. Basic Functionality Test

```python
# test_finance_domain.py
import requests
import json

BASE_URL = "http://localhost:8003"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["service"] == "FINANCE"

def test_domain_info():
    response = requests.get(f"{BASE_URL}/domain-info")
    data = response.json()
    assert data["domain_name"] == "FINANCE"
    assert "budgeting" in data["custom_config"]["topics"]

def test_chat():
    response = requests.post(f"{BASE_URL}/chat", json={
        "messages": [
            {"role": "user", "content": "What is our expense policy?"}
        ],
        "stream": False
    })
    assert response.status_code == 200

def test_glossary():
    # Add a finance term
    response = requests.post(f"{BASE_URL}/glossary/terms", json={
        "term": "EBITDA",
        "definition": "Earnings Before Interest, Taxes, Depreciation, and Amortization",
        "category": "metrics",
        "examples": ["EBITDA = Revenue - Operating Expenses"]
    })
    assert response.status_code == 200

# Run tests
if __name__ == "__main__":
    test_health()
    test_domain_info()
    test_chat()
    test_glossary()
    print("All tests passed!")
```

### 2. Custom Endpoints Test

```python
def test_finance_calculations():
    # Test ROI calculation
    response = requests.post(f"{BASE_URL}/finance/calculate/roi", json={
        "investment": 10000,
        "returns": 12000
    })
    data = response.json()
    assert data["roi_percentage"] == 20.0
    
    # Test compound interest
    response = requests.post(f"{BASE_URL}/finance/calculate/compound-interest", json={
        "principal": 1000,
        "rate": 5,
        "time": 10,
        "frequency": 12
    })
    assert response.status_code == 200
```

## Best Practices

### 1. Domain Naming Convention
- Use clear, single-word names: `finance`, `legal`, `sales`
- Keep names lowercase in code, uppercase in display
- Avoid abbreviations unless widely recognized

### 2. Configuration Structure
```python
custom_config = {
    # Basic Information
    "topics": "...",           # What the domain covers
    "systems": "...",          # Related systems/tools
    
    # Functional Settings
    "features": {...},         # Domain-specific features
    "limits": {...},          # Any restrictions
    
    # Integration Points
    "apis": {...},            # External services
    "databases": {...},       # Data sources
}
```

### 3. Template Organization
```
domains/finance/templates/
├── system_prompt.txt         # Main AI personality
├── query_enhancement.txt     # Query preprocessing
├── answer_generation.txt     # Response formatting
├── error_messages.txt        # Custom error messages
└── examples/                 # Example interactions
    ├── expense_query.txt
    └── budget_analysis.txt
```

### 4. Glossary Best Practices
- Pre-populate with common domain terms
- Use consistent categorization
- Include examples for complex terms
- Link related terms
- Regular review and updates

### 5. Security Considerations
```python
def validate_finance_request(request_data):
    """Validate finance-specific requests"""
    # Check for SQL injection in report parameters
    # Validate numerical inputs
    # Verify user permissions for sensitive data
    # Log all financial data access
    pass
```

### 6. Performance Optimization
- Cache frequently requested reports
- Pre-calculate common metrics
- Use pagination for large datasets
- Implement rate limiting for expensive operations

### 7. Error Handling
```python
@self.app.exception_handler(FinanceException)
async def handle_finance_error(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Finance calculation error",
            "detail": str(exc),
            "error_code": "FIN_CALC_001"
        }
    )
```

## Next Steps

1. **Deploy Your Domain**
   ```bash
   python start_domain_service.py finance --port 8003
   ```

2. **Add Initial Glossary**
   ```bash
   python scripts/import_glossary.py finance finance_terms.csv
   ```

3. **Configure Monitoring**
   - Set up alerts for critical errors
   - Monitor performance metrics
   - Track usage patterns

4. **Document Your Domain**
   - Create user guide
   - Document API endpoints
   - Provide example queries

5. **Integrate with Systems**
   - Connect to domain-specific databases
   - Set up data synchronization
   - Implement webhooks for updates

## Example Domains

Here are more examples of domains you might add:

- **Legal**: Contract management, compliance tracking, legal research
- **Sales**: CRM integration, lead tracking, sales analytics
- **Marketing**: Campaign management, content planning, analytics
- **Operations**: Process optimization, resource planning, logistics
- **Engineering**: Technical documentation, code reviews, architecture

Each domain can be customized to match your organization's specific needs and workflows.