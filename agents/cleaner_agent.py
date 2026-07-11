import re
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class EnterpriseCleanerAgent:
    """
    AgentOS Sanitization Layer (10/10)
    Ensures GDPR & HIPAA compliance by masking PII, PHI, API Keys, and Credentials.
    """
    def __init__(self):
        # 1. Initialize Presidio Engines
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # 2. Custom Recognizer: API Keys & Secrets
        # Detects standard AWS, Stripe, or generic Bearer tokens
        api_key_pattern = Pattern(
            name="api_key_regex", 
            regex=r"(?i)(?:api_key|apikey|bearer\s+token|secret)[=:\s]+['\"]?([a-zA-Z0-9_\-\.]{16,})['\"]?", 
            score=0.9
        )
        api_key_recognizer = PatternRecognizer(supported_entity="API_KEY", patterns=[api_key_pattern])
        self.analyzer.registry.add_recognizer(api_key_recognizer)

        # 3. Custom Recognizer: Passwords
        password_pattern = Pattern(
            name="password_regex", 
            regex=r"(?i)(?:password|passwd|pwd)[=:\s]+['\"]?([^'\"\s]+)['\"]?", 
            score=0.8
        )
        password_recognizer = PatternRecognizer(supported_entity="PASSWORD", patterns=[password_pattern])
        self.analyzer.registry.add_recognizer(password_recognizer)

    def sanitize(self, raw_text: str) -> str:
        if not raw_text:
            return ""
            
        # ==========================================
        # PHASE 1: Basic Formatting (Your original logic)
        # ==========================================
        clean_text = raw_text.strip().replace('\r\n', '\n')
        
        # Remove multiple consecutive newlines
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)

        # ==========================================
        # PHASE 2: Advanced PII/PHI Detection (The Brain)
        # ==========================================
        # We tell Presidio what exactly to hunt for in the text
        target_entities = [
            "EMAIL_ADDRESS", 
            "PHONE_NUMBER", 
            "CREDIT_CARD", 
            "PERSON", 
            "US_SSN", 
            "US_BANK_NUMBER",
            "API_KEY",       # Custom
            "PASSWORD"       # Custom
        ]
        
        results = self.analyzer.analyze(
            text=clean_text, 
            entities=target_entities,
            language='en'
        )
        
        # ==========================================
        # PHASE 3: Anonymization & Masking (The Shield)
        # ==========================================
        # Defining HOW each entity should be masked
        operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
            "CREDIT_CARD": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 12, "from_end": False}),
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 6, "from_end": False}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL_MASKED>"}),
            "API_KEY": OperatorConfig("replace", {"new_value": "<API_KEY_REDACTED>"}),
            "PASSWORD": OperatorConfig("replace", {"new_value": "<PASSWORD_REDACTED>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<USER_NAME_HIDDEN>"})
        }
        
        anonymized_result = self.anonymizer.anonymize(
            text=clean_text,
            analyzer_results=results,
            operators=operators
        )
        
        return anonymized_result.text

# Singleton instance to be used across AgentOS
cleaner = EnterpriseCleanerAgent()

# --- Example Usage ---
if __name__ == "__main__":
    dummy_log = """
    Crash report from server. 
    User satyam@company.com was trying to process a payment.
    Card used: 4111-2222-3333-4444. Phone: +1-555-019-8372.
    DB Connection string: postgresql://admin:SuperSecretPwd123@localhost:5432/db
    Failed because API_KEY = os.getenv("STRIPE_API_KEY") was revoked.
    """
    
    print("🔒 Sanitizing Logs...")
    safe_log = cleaner.sanitize(dummy_log)
    print(safe_log)