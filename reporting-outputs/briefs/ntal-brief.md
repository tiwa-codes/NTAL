# NTAL Telehealth MVP
**Inclusive, safe telehealth via USSD/SMS/WhatsApp and an offline-first CHW app**

## Objective

Provide accessible, equitable healthcare consultations to underserved populations through multi-channel telehealth access (USSD for feature phones, SMS, WhatsApp, and web), with a store-and-forward triage model that enables asynchronous consultations. The platform prioritizes offline-first capabilities for community health workers (CHWs) in low-connectivity areas, with built-in consent management and FHIR-based clinical data standards for interoperability.

## Target Population

- **Primary**: Rural and underserved communities with limited internet access
- **Secondary**: Patients using feature phones (non-smartphones)
- **Healthcare Providers**: Doctors, nurses, and community health workers (CHWs)
- **Geographic Focus**: Areas with unreliable internet connectivity requiring offline-first solutions

## Key Outputs & KPIs

| Output Category | Description | Current Status | Target KPIs |
|----------------|-------------|----------------|-------------|
| **Multi-Channel Access** | USSD, SMS, WhatsApp, IVR, Web interfaces | Adapters implemented (stubs ready) | *[TBD: 5,000+ users across channels]* |
| **Store-and-Forward Triage** | Asynchronous patient-provider consultations | ✅ Fully functional | *[TBD: 1,000+ encounters/month]* |
| **CHW Offline-First App** | Progressive Web App (PWA) for offline use | ✅ Implemented with service workers | *[TBD: 50+ active CHWs]* |
| **Provider Dashboard** | Case management, filtering, and triage tools | ✅ Operational | *[TBD: 10+ healthcare facilities]* |
| **FHIR Integration** | Standards-based clinical data exchange | 🔄 Roadmap item | *[TBD: 3+ EMR integrations]* |
| **Consent Management** | Privacy-by-design audit logging | 🔄 Roadmap item | 100% compliant encounters |
| **Security & Authentication** | JWT-based provider auth, bcrypt hashing | ✅ Implemented | Zero security breaches |

**Note**: Metrics marked with *[TBD]* are placeholders. Update with actual usage data from production deployment logs, database queries (`SELECT COUNT(*) FROM encounters`), and analytics dashboards.

## Key Learnings & Adaptations

- **Multi-channel adapter architecture**: Developed extensible adapter pattern for USSD, SMS, WhatsApp, and IVR to enable rapid integration with telecom providers
- **Offline-first prioritization**: PWA implementation with service workers ensures CHWs can access patient data in zero-connectivity scenarios
- **Store-and-forward model**: Asynchronous triage reduces real-time bandwidth requirements while maintaining quality of care
- **Technology stack choices**: FastAPI + React + TypeScript provides type safety and developer velocity; SQLite for dev, PostgreSQL for production
- **Docker containerization**: Simplified deployment across diverse infrastructure environments
- **Open standards commitment**: FHIR readiness in roadmap to ensure interoperability with existing health information systems

## Top 3 Recommended Next Steps

1. **Implement real-world channel integrations**
   - Partner with local telecom providers to activate USSD, SMS, and WhatsApp adapters
   - Conduct pilot programs with 2-3 rural health facilities to test multi-channel access
   - Target: 500+ patients reached via feature phone channels within 3 months

2. **Deploy FHIR-based data exchange**
   - Complete FHIR R4 integration for encounters, patients, and observations
   - Establish secure API connections with 1-2 existing EMR systems in target regions
   - Ensure consent management and audit logging are production-ready

3. **Scale CHW offline capabilities**
   - Expand offline data sync capabilities to handle higher volumes
   - Develop training materials and onboarding program for CHWs
   - Monitor offline sync performance and optimize for low-bandwidth scenarios
   - Target: 50+ trained CHWs actively using the platform within 6 months

---

*For questions or updates to this brief, contact the NTAL development team or open an issue at: https://github.com/tiwa-codes/NTAL*

**Version**: 1.0 | **Last Updated**: November 2025 | **Status**: MVP Ready for Pilot Deployment
