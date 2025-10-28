# Feature Specification: PrepSmart Multi-Agent Crisis Preparedness Assistant

**Feature Branch**: `001-prepsmart-mvp`
**Created**: 2025-10-28
**Status**: Draft
**Input**: Multi-agent AI crisis preparedness assistant that helps people survive both natural disasters AND economic emergencies. Timely response to Hurricane Melissa (Category 5, Jamaica) and US Government Shutdown (900k+ workers affected). MVP deadline: Oct 31, 2025 (4 days) for AI Bootcamp hackathon.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Disaster Preparedness Plan (Priority: P1)

A person facing an imminent natural disaster (hurricane, earthquake, wildfire, etc.) visits PrepSmart, enters their location and basic household info, and within 5 minutes receives a comprehensive, personalized preparedness plan including risk assessment, supply checklist, family emergency plan, and local resources.

**Why this priority**: This is the core life-saving value proposition. Hurricane Melissa is happening NOW. This single journey must demonstrate the multi-agent system working together to deliver actionable, personalized guidance that could save lives.

**Independent Test**: Can be fully tested by entering a ZIP code in a hurricane zone (e.g., Kingston, Jamaica or Miami, FL), selecting "Hurricane" as crisis type, completing the household questionnaire, and receiving a complete PDF plan with risk levels, supply lists, evacuation info, and local shelter locations.

**Acceptance Scenarios**:

1. **Given** a user visits PrepSmart landing page, **When** they select "Natural Disaster" and enter ZIP code in hurricane zone, **Then** system displays EXTREME risk level for hurricanes with severity score
2. **Given** user has entered location and crisis type, **When** they complete household questionnaire (adults: 2, children: 1, pets: 1, budget: $100), **Then** Coordinator Agent triggers all relevant specialist agents in parallel
3. **Given** agents are processing, **When** user views progress screen, **Then** system displays real-time status for each active agent (Risk Assessment, Supply Planning, Resource Locator, Video Curator, Documentation)
4. **Given** all agents have completed analysis, **When** user views results, **Then** system displays prioritized supply checklist organized by Critical/Prepared/Comprehensive tiers, all within $100 budget
5. **Given** supply plan is complete, **When** user reviews family emergency plan, **Then** system shows evacuation routes, meeting points, emergency contacts template, and communication plan specific to their household composition
6. **Given** complete plan is ready, **When** user clicks "Download Plan", **Then** system generates professional PDF with all sections, ready for offline access
7. **Given** user wants educational content, **When** they view video recommendations, **Then** system displays 5-7 relevant videos from FEMA, Red Cross, and YouTube experts specific to hurricane preparedness

---

### User Story 2 - Economic Crisis Survival Plan (Priority: P2)

A federal worker affected by the government shutdown (or someone facing unemployment/layoff) visits PrepSmart, selects "Economic Crisis", enters their financial situation, and receives a 30-day survival budget, benefits eligibility assessment, hardship letter templates, and local assistance resources.

**Why this priority**: The US Government shutdown is affecting 900k+ workers RIGHT NOW. This demonstrates PrepSmart's unique value beyond typical disaster prep apps. Many people face economic crises but don't know where to start.

**Independent Test**: Can be fully tested by selecting "Government Shutdown" as crisis type, entering financial details (income: $0, expenses: $3000/month, savings: $2000, dependents: 2), and receiving a complete 30-day action plan with budget breakdown, benefits guide, and assistance resources.

**Acceptance Scenarios**:

1. **Given** a user selects "Economic Crisis" mode, **When** they choose "Government Shutdown" as crisis type, **Then** system displays Financial Advisor Agent activation and begins guided questionnaire
2. **Given** user enters financial situation (current income, monthly expenses, available savings, debt obligations), **When** they submit details, **Then** system categorizes expenses into Must-Pay/Defer/Eliminate buckets
3. **Given** Financial Advisor has analyzed situation, **When** user views 30-day plan, **Then** system displays day-by-day action items (Day 1: Contact landlord, Day 2: File unemployment, Day 3: Apply for SNAP, etc.)
4. **Given** user needs to communicate with creditors, **When** they access hardship letter templates, **Then** system provides pre-filled templates for landlord, credit cards, utilities, student loans with user's specific situation
5. **Given** user wants to know benefits eligibility, **When** they view benefits section, **Then** system shows personalized assessment for unemployment insurance, SNAP, Medicaid, utility assistance with estimated amounts and application links
6. **Given** user needs local help, **When** Resource Locator Agent completes, **Then** system displays map and list of nearby food banks, free legal aid, unemployment offices, and community assistance programs
7. **Given** complete economic plan is ready, **When** user downloads PDF, **Then** document includes budget spreadsheet, action timeline, letter templates, benefits checklist, and resource contacts

---

### User Story 3 - Multi-Agent System Demonstration (Priority: P1)

A hackathon judge or demo viewer watches PrepSmart process a crisis scenario and clearly sees the multi-agent orchestration in action, with each agent's role, activity, and contribution to the final plan visible and understandable.

**Why this priority**: This is a hackathon project showcasing Microsoft Agent Framework. The multi-agent collaboration must be VISIBLE and IMPRESSIVE. Judges need to understand how 7 agents work together seamlessly.

**Independent Test**: Can be demonstrated by starting any crisis plan and watching the agent activity dashboard show each agent activating, processing, and completing their specialized tasks with progress indicators and handoff points.

**Acceptance Scenarios**:

1. **Given** user submits crisis questionnaire, **When** Coordinator Agent receives request, **Then** system displays orchestration dashboard showing Coordinator evaluating the scenario and dispatching specialist agents
2. **Given** Coordinator has triaged request, **When** specialist agents activate, **Then** UI shows each agent with icon, name, description of role, and real-time status (Waiting/Active/Complete)
3. **Given** Risk Assessment Agent is working, **When** judge views details, **Then** system explains "Analyzing weather data, historical patterns, and geographic vulnerabilities for your location" with progress bar
4. **Given** multiple agents are running, **When** Supply Planning Agent requests data from Risk Assessment, **Then** system shows inter-agent communication with message: "Supply Planning Agent requesting risk level from Risk Assessment Agent"
5. **Given** Supply Planning Agent completes, **When** Documentation Agent starts, **Then** system shows handoff: "Supply Planning complete. Documentation Agent now compiling plan..."
6. **Given** an agent encounters error, **When** failure occurs, **Then** system gracefully degrades, shows error to user, and continues with other agents (e.g., "Video Curator unavailable - proceeding with core plan")
7. **Given** all agents complete successfully, **When** final plan displays, **Then** system shows summary of each agent's contribution with timestamps and clear attribution

---

### User Story 4 - Mobile-Responsive Emergency Access (Priority: P2)

A person in a crisis situation accesses PrepSmart from their mobile phone (potentially on a spotty connection) and can still complete the questionnaire and view their plan with large, tappable buttons and readable text.

**Why this priority**: Many people in disaster zones or economic hardship only have mobile phones. Hurricane evacuees may be on the road. Unemployed workers may not have laptop access. Mobile-first is essential for equity and accessibility.

**Independent Test**: Can be tested by accessing PrepSmart on iPhone/Android (or browser DevTools mobile emulation), completing full natural disaster flow on 3G throttled connection, and verifying all content is readable, all buttons are tappable (44px+ touch targets), and plan downloads successfully.

**Acceptance Scenarios**:

1. **Given** user visits PrepSmart on mobile device, **When** landing page loads, **Then** hero section, crisis type buttons, and call-to-action are fully visible without horizontal scrolling
2. **Given** user is on mobile with slow connection, **When** questionnaire form loads, **Then** form fields are large (minimum 44px touch targets), labels are readable (16px+ font), and page loads in under 5 seconds
3. **Given** user is filling out form on mobile, **When** they tap input fields, **Then** appropriate keyboard appears (numeric for numbers, email for email) and form doesn't jump/resize
4. **Given** agents are processing on mobile, **When** user views agent dashboard, **Then** agent cards stack vertically, status indicators are clear, and progress bars are visible
5. **Given** plan is ready on mobile, **When** user views results, **Then** sections are collapsible/expandable, text is readable without zooming, and PDF download works (opens in mobile browser or downloads)
6. **Given** user has limited bandwidth, **When** page includes images/videos, **Then** images are optimized, videos are links (not embeds), and core functionality works without heavy assets
7. **Given** user navigates on mobile, **When** they tap navigation elements, **Then** buttons are clearly clickable with adequate spacing, no accidental clicks, and touch feedback is immediate

---

### User Story 5 - Personalized Supply Planning with Budget Tiers (Priority: P3)

A family with limited funds needs to prepare for a disaster but can't afford the typical "ultimate survival kit" recommendations. They specify a $50 budget and receive a realistic, prioritized supply list that maximizes safety within their constraints.

**Why this priority**: Economic crisis awareness is core to PrepSmart's mission. Showing wealthy people a $500 prep list is easy. Helping a struggling family prep for $50 is what makes PrepSmart inclusive and life-saving for everyone.

**Independent Test**: Can be tested by completing disaster prep flow with budget set to $50, and verifying the supply list contains only Critical-tier items, includes specific product recommendations with prices, suggests free alternatives (public water fill stations vs. bottled water), and totals under $50.

**Acceptance Scenarios**:

1. **Given** user selects budget tier of $50, **When** Supply Planning Agent generates list, **Then** system returns ONLY Critical tier items (water, non-perishable food, first aid, flashlight, radio, batteries)
2. **Given** user has budget of $100, **When** plan generates, **Then** system includes Critical + Prepared tier items (adding hygiene supplies, extra batteries, basic tools, copies of documents)
3. **Given** user has budget of $200+, **When** plan generates, **Then** system includes all three tiers (adding comprehensive items like generator, extended food supply, specialty gear)
4. **Given** user views supply list, **When** they see each item, **Then** display shows item name, quantity needed (adjusts for household size), estimated price, and substitution suggestions
5. **Given** user has very limited budget, **When** system suggests water, **Then** recommendations include free alternatives: "Fill clean containers at home (FREE) or buy 12-pack for $4.99"
6. **Given** supply list exceeds budget slightly, **When** user views total, **Then** system highlights: "Total: $54.32 (slightly over $50 budget)" and suggests "Remove [lowest priority item] to stay under budget"
7. **Given** user wants to understand prioritization, **When** they tap info icon on tier, **Then** system explains: "Critical: Immediate survival needs (72 hours). Prepared: Extended safety (1 week). Comprehensive: Maximum readiness (2+ weeks)"

---

### Edge Cases

- **What happens when user enters invalid ZIP code?** System displays error: "Unable to find location data for ZIP code. Please verify and try again, or enter city/state manually."
- **What happens when multiple disaster types threaten same location (e.g., earthquake AND wildfire zone)?** Risk Assessment Agent ranks all threats, plan includes guidance for top 2 threats, notes combined risk scenarios.
- **What happens when Claude API rate limit is hit?** System falls back to cached responses for common scenarios or displays: "High demand detected. Your plan will be ready in 2-3 minutes. We'll email when complete."
- **What happens when user has $0 budget for supplies?** System focuses entirely on free resources: public shelters, free meal programs, community supply distributions, items to gather from home.
- **What happens when user's location has no nearby resources?** Resource Locator Agent expands search radius to 50 miles, includes national hotlines, virtual resources, and notes transportation options.
- **What happens when user clicks "Download PDF" but generation fails?** System retries once, if fails again: "PDF generation error. You can copy/paste your plan from screen or email yourself the link."
- **What happens when user abandons form halfway?** System saves progress in local storage, shows "Resume Plan" button on return. No server-side storage for privacy.
- **What happens when government shutdown ends during user's plan?** User can update crisis status, Financial Advisor Agent adjusts plan to "Return to work preparation mode" with new guidance.
- **What happens when agent takes longer than 30 seconds?** System shows "This is taking longer than expected..." message with option to continue waiting or skip that agent's contribution.
- **What happens when user has complex household (6 adults, 3 children, 4 pets)?** Supply calculations scale appropriately, system warns if total supply cost exceeds any budget tier, suggests community pooling resources.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support two crisis modes: Natural Disaster (hurricane, earthquake, wildfire, flood, tornado, blizzard) and Economic Crisis (government shutdown, unemployment, layoff, furlough)
- **FR-002**: System MUST collect user location via ZIP code or city/state and validate against geographic database
- **FR-003**: System MUST collect household composition (number of adults, children, pets), housing type (apartment, house, mobile home), and budget constraint ($50, $100, $200+)
- **FR-004**: System MUST implement 7 specialized AI agents using Microsoft Agent Framework: Coordinator, Risk Assessment, Supply Planning, Financial Advisor, Resource Locator, Video Curator, Documentation
- **FR-005**: System MUST display real-time agent activity with status indicators (Waiting/Active/Complete) and plain-language descriptions of each agent's current task
- **FR-006**: System MUST generate risk assessment with severity levels (EXTREME/HIGH/MEDIUM/LOW) and specific threat analysis for user's location
- **FR-007**: System MUST create personalized supply checklist organized by three budget tiers (Critical/Prepared/Comprehensive) with items scaled to household size
- **FR-008**: System MUST generate family emergency plan including evacuation routes, meeting points, emergency contact template, and communication strategy
- **FR-009**: System MUST identify local resources (shelters, food banks, unemployment offices) within user's area using geographic search
- **FR-010**: System MUST recommend 5-7 relevant educational videos from FEMA, Red Cross, YouTube, and other authoritative sources
- **FR-011**: System MUST generate downloadable PDF document containing complete preparedness plan with all sections
- **FR-012**: System MUST create 30-day economic survival plan with day-by-day action items when Economic Crisis mode is selected
- **FR-013**: System MUST categorize user expenses into Must-Pay (rent, utilities), Defer (credit cards), and Eliminate (subscriptions) buckets
- **FR-014**: System MUST provide hardship letter templates pre-filled with user's situation for landlords, creditors, and utility companies
- **FR-015**: System MUST assess benefits eligibility (unemployment insurance, SNAP, Medicaid) with estimated amounts and application links
- **FR-016**: System MUST be mobile-responsive with minimum 44px touch targets, readable font sizes (16px+), and work on 3G connections
- **FR-017**: System MUST implement graceful degradation when individual agents fail, allowing other agents to continue and delivering partial plan if needed
- **FR-018**: System MUST complete full plan generation in under 5 minutes (target: 2-3 minutes)
- **FR-019**: System MUST use HTTPS for all API communication and not store sensitive user financial data
- **FR-020**: System MUST provide clear disclaimers that PrepSmart is an AI assistant and not a replacement for professional emergency management or financial advice
- **FR-021**: System MUST cite authoritative sources (FEMA, CDC, Red Cross, government agencies) for all recommendations
- **FR-022**: System MUST implement offline-capable core functionality with critical checklists available without internet
- **FR-023**: System MUST save user progress in browser local storage if they abandon form, with option to resume
- **FR-024**: System MUST support both English language (MVP) with roadmap for Spanish [NEEDS CLARIFICATION: Spanish translation priority for v2?]
- **FR-025**: System MUST log all agent interactions and errors for debugging and quality improvement [NEEDS CLARIFICATION: logging infrastructure - Application Insights, local files, or both?]

### Key Entities

- **Crisis Profile**: Represents a user's crisis scenario including crisis type (natural disaster or economic), specific threat (hurricane, shutdown, etc.), location (ZIP/city/state), household composition (adults, children, pets), housing type, budget constraint, and timestamp of creation.

- **Risk Assessment**: Represents the evaluated threat level for a location including severity score (0-100), risk level (EXTREME/HIGH/MEDIUM/LOW), specific threats identified (e.g., "Category 5 hurricane within 100 miles"), historical data context, and affected geographic area.

- **Supply Plan**: Represents the personalized preparedness supplies including three tiers (Critical, Prepared, Comprehensive), items with quantities adjusted for household size, estimated prices, substitution suggestions, total cost by tier, and specific recommendations based on crisis type.

- **Emergency Plan**: Represents the family's action plan including evacuation routes (primary and secondary), meeting points (local and out-of-town), emergency contact template, communication strategy (how family will contact each other), and special considerations (pets, medications, mobility needs).

- **Economic Plan**: Represents the 30-day survival strategy including budget breakdown (Must-Pay/Defer/Eliminate), day-by-day action timeline, benefits eligibility assessment, estimated relief amounts, hardship letter templates, and local assistance resources.

- **Resource Location**: Represents a local assistance resource including name, address, phone, hours of operation, services offered, distance from user, and resource type (shelter, food bank, unemployment office, etc.).

- **Video Recommendation**: Represents an educational video including title, source (FEMA, Red Cross, YouTube channel), URL, duration, relevance score to user's crisis, and brief description of content.

- **Agent Activity Log**: Represents the real-time status of each agent including agent name, current status (Waiting/Active/Complete/Error), start time, completion time, current task description, progress percentage, and any inter-agent communications.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete crisis questionnaire and receive a full preparedness plan in under 5 minutes (target: 3 minutes average)
- **SC-002**: System successfully generates plans for 100% of valid US ZIP codes for natural disaster scenarios
- **SC-003**: 90% of users report (via post-plan survey) that the plan is actionable and gives them concrete next steps
- **SC-004**: Multi-agent orchestration is visible and understandable, with 80%+ of demo viewers able to identify at least 3 different agent roles
- **SC-005**: System handles 100 concurrent users without agent response time exceeding 30 seconds
- **SC-006**: PDF generation succeeds on first attempt for 95%+ of completed plans
- **SC-007**: Mobile experience is fully functional with 100% of core features accessible on viewport widths from 320px to 428px
- **SC-008**: Supply plans stay within user's specified budget tier for 90%+ of generated lists
- **SC-009**: System gracefully handles individual agent failures with degraded plan delivered in 100% of partial failure scenarios
- **SC-010**: All recommendations are backed by authoritative sources with 100% of advice traceable to FEMA, CDC, Red Cross, or government guidance
- **SC-011**: Economic crisis plans include minimum 20 specific action items with deadlines and resources for every scenario
- **SC-012**: For hackathon demo: Plan generation impresses judges with clear multi-agent collaboration, real-world applicability, and technical sophistication
- **SC-013**: Page load time is under 3 seconds on 3G connection (tested with Chrome DevTools throttling)
- **SC-014**: Accessibility score of 90+ on Lighthouse audit for mobile and desktop versions
- **SC-015**: Zero sensitive user data (financial details, personal info) stored in database beyond session duration

### Non-Functional Requirements

- **NFR-001**: System must be deployable to Azure Container Apps free tier without exceeding resource limits
- **NFR-002**: Claude API costs must not exceed $50 for 1000 plan generations (estimate $0.05 per plan)
- **NFR-003**: All code must have type hints (Python) and pass linting (Ruff for Python, ESLint for JavaScript)
- **NFR-004**: Agent architecture must be modular allowing individual agents to be updated/replaced without affecting others
- **NFR-005**: System must be demonstrable offline for hackathon presentation (with recorded agent flows if live APIs unavailable)

## Clarifications

[NEEDS CLARIFICATION: Should the system support creating accounts and saving multiple plans, or is it one-time anonymous usage for MVP?]

[NEEDS CLARIFICATION: For the Video Curator Agent, should we use YouTube Data API (requires API key) or scrape/curate a static list of high-quality videos?]

[NEEDS CLARIFICATION: Should the Resource Locator Agent use Google Maps API (costs money) or OpenStreetMap (free but less comprehensive)?]

[NEEDS CLARIFICATION: What's the priority for additional natural disaster types beyond hurricane? Should MVP support all 6 types (hurricane, earthquake, wildfire, flood, tornado, blizzard) or focus on 2-3?]

[NEEDS CLARIFICATION: For hackathon demo, do we need real agent processing or can we simulate agent activity with pre-generated responses to ensure reliable demo?]

[NEEDS CLARIFICATION: Should we support multiple languages in MVP, or is English-only acceptable with internationalization architecture for future?]

## Review & Acceptance Checklist

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain (6 clarifications needed above)
- [ ] All requirements are testable and unambiguous
- [ ] Success criteria are measurable and realistic for 4-day timeline
- [ ] Edge cases cover major failure scenarios

### Constitutional Compliance
- [ ] Life-Saving Priority (Article I): Critical information flow is clear in user stories
- [ ] Accessibility & Inclusion (Article II): Mobile-first design specified, budget consciousness embedded
- [ ] Multi-Agent Transparency (Article III): User Story 3 explicitly demonstrates agent visibility
- [ ] Data Privacy (Article IV): FR-019 addresses security, FR-025 clarifies logging
- [ ] Budget-Consciousness (Article V): Supply plan tiers in User Story 5, economic crisis focus
- [ ] Evidence-Based (Article VI): FR-021 requires source citation
- [ ] Speed & Simplicity (Article VII): 5-minute target in SC-001, minimal questionnaire
- [ ] Test-First (Article VIII): Will be enforced during implementation phase
- [ ] Graceful Degradation (Article IX): FR-017 specifies agent failure handling

### Scope Management
- [ ] MVP scope is achievable in 4 days (Oct 27-31)
- [ ] P1 priorities deliver standalone value if P2/P3 are cut
- [ ] Technical stack aligns with hackathon constraints (Azure, Python, Flask, Microsoft Agent Framework)
- [ ] Clarifications identified for user to resolve before implementation plan

### Hackathon Readiness
- [ ] Multi-agent demonstration value is clear (User Story 3)
- [ ] Real-world problem urgency is evident (Hurricane Melissa, Government Shutdown)
- [ ] Technical sophistication is showcase-worthy (7 agents, orchestration, PDF generation)
- [ ] Demo-ability is considered (NFR-005 for offline fallback)

**Next Steps**:
1. User reviews and provides clarifications for 6 [NEEDS CLARIFICATION] items
2. User validates constitutional compliance and hackathon alignment
3. Once approved, proceed to `/speckit.plan` to define technical implementation
