# Kong Gateway Plugins vs API Security Standards

| Plugin Name                 | Category           | Description                                        | GDPR      | HIPAA     | PCI-DSS   | ISO 27001   | OWASP API Top 10   | PSD2/SCA   | PIPEDA    | NIST      | SOC 2     |
|:----------------------------|:-------------------|:---------------------------------------------------|:----------|:----------|:----------|:------------|:-------------------|:-----------|:----------|:----------|:----------|
| JWT Authentication          | Authentication     | Token-based identity verification                  | Mandatory | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Mandatory | Mandatory | Mandatory |
| OAuth2 / OpenID Connect     | Authentication     | Federated identity and delegated access            | Mandatory | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Mandatory | Mandatory | Mandatory |
| Mutual TLS Authentication   | Authentication     | Certificate-based client-server authentication     | Mandatory | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Mandatory | Mandatory | Mandatory |
| Basic Authentication        | Authentication     | Simple username/password-based access              | Optional  | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |
| Key Authentication          | Authentication     | API key-based access control                       | Optional  | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |
| ACL (Access Control List)   | Authorization      | Role-based access control                          | Mandatory | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Mandatory | Mandatory | Mandatory |
| IP Restriction              | Authorization      | Restrict access based on IP address                | Optional  | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |
| Rate Limiting               | Threat Protection  | Prevent abuse and DoS attacks                      | Optional  | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Optional  | Mandatory | Mandatory |
| Request Size Limiting       | Threat Protection  | Prevent resource exhaustion                        | Optional  | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |
| Bot Detection               | Threat Protection  | Detect and block automated threats                 | Optional  | Optional  | Optional  | Optional    | Mandatory          | Optional   | Optional  | Mandatory | Optional  |
| Request Validator           | Input Validation   | Enforce schema validation                          | Mandatory | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Mandatory | Mandatory | Mandatory |
| CORS                        | Access Control     | Restrict cross-origin access                       | Mandatory | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |
| Response Transformer        | Data Protection    | Modify or sanitize API responses                   | Mandatory | Mandatory | Optional  | Optional    | Optional           | Optional   | Mandatory | Optional  | Optional  |
| Exit Transformer            | Data Protection    | Obfuscate or transform final responses             | Optional  | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |
| Logging Plugins (TCP/HTTP)  | Monitoring & Audit | Log API traffic for auditing and compliance        | Mandatory | Mandatory | Mandatory | Mandatory   | Optional           | Mandatory  | Mandatory | Mandatory | Mandatory |
| PII Sanitizer (AI Plugin)   | Data Protection    | Mask or redact personally identifiable information | Mandatory | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Mandatory | Mandatory | Mandatory |
| Developer Portal            | Access Governance  | Secure access to API documentation and onboarding  | Mandatory | Mandatory | Mandatory | Mandatory   | Mandatory          | Mandatory  | Mandatory | Mandatory | Mandatory |
| AWS Guardrails (AI Plugin)  | AI Content Safety  | Validate AI-generated content for compliance       | Optional  | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |
| Azure Content Safety Plugin | AI Content Safety  | Moderate and filter unsafe content                 | Optional  | Optional  | Optional  | Optional    | Optional           | Optional   | Optional  | Optional  | Optional  |


## API Security Standards Overview

### GDPR (General Data Protection Regulation)
European Union regulation focused on data protection and privacy for individuals. Requires secure handling of personal data, consent management, and breach notification.

### HIPAA (Health Insurance Portability and Accountability Act)
US regulation for protecting sensitive patient health information. Requires access controls, audit logging, and data integrity.

### PCI-DSS (Payment Card Industry Data Security Standard)
Global standard for securing credit card transactions. Requires strong authentication, encryption, and monitoring.

### ISO 27001
International standard for information security management systems. Emphasizes risk management, access control, and continuous improvement.

### OWASP API Security Top 10
Community-driven list of top API security risks including broken authentication, excessive data exposure, and injection flaws.

### PSD2 & SCA (Payment Services Directive 2 & Strong Customer Authentication)
EU regulation for secure electronic payments. Requires multi-factor authentication and secure communication.

### PIPEDA (Personal Information Protection and Electronic Documents Act)
Canadian law governing data privacy. Requires consent, data protection, and breach notification.

### NIST (National Institute of Standards and Technology)
US framework for cybersecurity including SP 800-228 for API security. Emphasizes Zero Trust, DevSecOps, and lifecycle protection.

### SOC 2
US standard for managing customer data based on five trust principles: security, availability, processing integrity, confidentiality, and privacy.
