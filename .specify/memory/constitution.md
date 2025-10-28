# PrepSmart Constitution

## Core Principles

### I. Life-Saving Priority
**Every design decision must prioritize human life and safety above technical elegance.**

- Critical information (emergency contacts, evacuation routes, urgent warnings) must be immediately visible
- No feature should delay access to life-saving information
- Fail-safe defaults: if data is unavailable, show conservative worst-case guidance
- Offline-first mindset: core emergency info must work without internet

### II. Accessibility & Inclusion
**Emergency preparedness tools must be accessible to all people, regardless of technical ability, economic status, or disability.**

- Mobile-first responsive design (many people only have phones)
- Clear, simple language (8th-grade reading level max)
- High contrast, large touch targets for accessibility
- Multi-language support roadmap (starting with English/Spanish)
- Works on low-bandwidth connections
- No paid features that gate life-saving information

### III. Multi-Agent Transparency
**Users must understand which AI agents are working and what they're doing.**

- Real-time agent activity display with clear status indicators
- Plain-language explanations of what each agent does
- Progress indicators for long-running operations
- Error messages that explain what went wrong and what to do next
- Agent handoffs must be seamless and logged

### IV. Data Privacy & Security
**User crisis data is sensitive and must be protected.**

- Minimal data collection (only what's needed for personalization)
- No selling or sharing of user data
- Clear privacy policy in plain language
- Secure API communication (HTTPS only)
- No tracking beyond basic analytics
- User can download/delete their data

### V. Budget-Consciousness
**Economic crisis planning must respect that users may have very limited funds.**

- Always provide multiple budget tiers ($50, $100, $200+)
- Free alternatives highlighted for every paid resource
- No affiliate links or sponsored products
- Transparent pricing in all recommendations
- Focus on what people already have vs what to buy

### VI. Evidence-Based Guidance
**All recommendations must be based on authoritative sources.**

- FEMA, CDC, Red Cross, and government agency guidance prioritized
- External resources must be vetted and current
- AI-generated advice must cite sources
- Regular content review to ensure accuracy
- Disclaimer: AI assistant, not replacement for professional advice

### VII. Speed & Simplicity
**Users in crisis need answers in minutes, not hours.**

- Target: Complete plan in under 5 minutes
- Progressive disclosure: most critical info first
- Minimal form fields (location, family size, budget)
- Smart defaults reduce choices
- Single-page flow where possible
- No unnecessary steps or "nice to have" features

### VIII. Test-First Development
**All features must have tests before implementation.**

- Unit tests for agent logic
- Integration tests for agent coordination
- End-to-end tests for critical user flows
- Test with realistic scenarios (Category 5 hurricane, sudden job loss)
- Manual testing with real users (bootcamp cohort, family members)

### IX. Graceful Degradation
**System must provide value even when components fail.**

- If one agent fails, others continue working
- Cached fallbacks for external APIs
- Static emergency checklists if AI unavailable
- Clear error messages with manual alternatives
- Health checks for all critical dependencies

## Technical Standards

### Agent Architecture
- Microsoft Agent Framework for orchestration
- Claude API (Anthropic) for AI reasoning
- Agent communication via message passing
- Each agent is independently testable
- Coordinator agent handles failure recovery

### Performance Requirements
- Initial page load: < 3 seconds
- Agent response time: < 30 seconds
- PDF generation: < 10 seconds
- Support 100 concurrent users (MVP)
- Mobile-first: works on 3G connections

### Technology Stack
- **Backend**: Python 3.11+, Flask
- **AI Framework**: Microsoft Agent Framework + Claude API
- **Frontend**: HTML/CSS/JavaScript (vanilla or lightweight framework)
- **Deployment**: Azure Container Apps (free tier)
- **Database**: SQLite for MVP (Postgres for production)
- **File Storage**: Azure Blob Storage for PDFs

### Code Quality
- Type hints for all Python functions
- Docstrings for all agents and public methods
- Linting: Ruff for Python, ESLint for JS
- Max function length: 50 lines
- DRY principle: shared agent utilities extracted

## Development Workflow

### Feature Development Process
1. **Specification**: Define user story and acceptance criteria
2. **Risk Assessment**: Identify life-safety implications
3. **Constitutional Review**: Verify alignment with principles
4. **Test Planning**: Write tests before implementation
5. **Implementation**: Build feature with TDD
6. **Real-World Testing**: Test with actual scenarios
7. **Documentation**: Update user guides and agent docs

### Quality Gates
- [ ] All tests passing (unit, integration, e2e)
- [ ] Constitutional compliance verified
- [ ] Accessibility tested (screen reader, keyboard nav)
- [ ] Mobile responsiveness confirmed
- [ ] Performance benchmarks met
- [ ] Security scan passed
- [ ] Real user tested (at least 2 people)

### Crisis-Specific Testing
- **Natural Disasters**: Test with real hurricane, earthquake, wildfire scenarios
- **Economic Crisis**: Test with actual government shutdown, layoff situations
- **Validation**: Compare AI output with FEMA/Red Cross official guidance

## Governance

### Amendment Process
This constitution can be amended when:
- New life-safety considerations are discovered
- User feedback reveals accessibility gaps
- Technical constraints change (API limits, framework updates)
- Real-world crisis response reveals flaws

Amendments require:
- Documentation of rationale and impact
- Review by both technical and domain experts
- Backwards compatibility assessment
- User communication of changes

### Conflict Resolution
When principles conflict:
1. **Life-Saving Priority** (Article I) overrides all others
2. **Accessibility** (Article II) overrides technical preferences
3. **Speed & Simplicity** (Article VII) overrides feature richness
4. Document the conflict and resolution in implementation plan

### Hackathon Constraints
For the MVP (Oct 27-31, 2025):
- Acceptable to have incomplete features if core value is delivered
- Focus on one disaster type + one economic scenario
- Use placeholder data for initial testing
- Document known limitations for future work

**Version**: 1.0.0 | **Ratified**: 2025-10-28 | **Last Amended**: 2025-10-28
