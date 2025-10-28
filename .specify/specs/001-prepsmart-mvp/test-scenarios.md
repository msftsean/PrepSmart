# PrepSmart MVP - Critical Test Scenarios

**Date**: 2025-10-28
**Purpose**: Define 5 realistic test scenarios that validate PrepSmart MVP functionality before hackathon demo

**Success Criteria**: Each scenario must complete in under 180 seconds with all agents succeeding and generating downloadable PDF.

---

## Scenario 1: High-Risk Natural Disaster, Low Budget
**Test ID**: TS-001
**Priority**: P0 (Blocker)
**User Story**: US1 (Natural Disaster Preparedness Plan)

### Input Profile
- **Crisis Mode**: Natural Disaster
- **Specific Threat**: Hurricane
- **Location**: Miami, FL 33101 (known hurricane zone)
- **Household**: 1 adult, 2 children, 0 pets
- **Housing Type**: Apartment
- **Budget Tier**: $50 (lowest)
- **Timing**: Peak hurricane season (September)

### Expected Agent Behavior

**Risk Assessment Agent**:
- Risk Level: EXTREME
- Severity Score: 90-100
- Threat: "Category 4-5 hurricane within 100 miles"
- Historical data: References Hurricane Andrew (1992), recent Category 5 storms
- Timeline: "Landfall expected within 48-72 hours"

**Supply Planning Agent**:
- Tier: Critical only (respects $50 hard limit)
- Items: 3 gallons water, 5 days non-perishable food, first aid kit, flashlight, batteries, battery radio
- Household scaling: Quantities adjusted for 3 people (1 adult + 2 children)
- Total cost: $48-50 (stays within budget)
- Recommendations: "Fill bathtub with water (FREE), charge all devices now"
- Warning displayed: "⚠️ EXTREME risk detected. $50 tier may not provide adequate protection. Recommend $100+ tier."
- User must explicitly choose whether to upgrade

**Financial Advisor Agent** (if applicable):
- Not heavily involved in natural disaster mode
- Quick check: "Do you have emergency funds for evacuation?"
- Suggests: Low-cost evacuation options (public shelter vs. hotel)

**Resource Locator Agent**:
- Find: Emergency shelters within Miami (10+ Red Cross shelters)
- Find: Supply stores (Walmart, Home Depot, CVS within 5 miles)
- Find: Hospitals (Jackson Memorial, Baptist Health)
- Find: Evacuation routes (I-95 North, Florida Turnpike)
- Distance: All within 20-mile radius
- Data source: Mix of static database + Google Places API for real-time store hours

**Video Curator Agent**:
- Return: 5-7 hurricane prep videos
- Sources: FEMA (1 video), Red Cross (1), Weather Channel (2), survival expert YouTubers (2)
- Total duration: Under 18 minutes combined
- All videos under 5 minutes each
- Topics: "How to prepare for a hurricane in 24 hours", "Evacuation tips with kids", "What to do if you can't evacuate"

**Documentation Agent**:
- Generate: 2-page PDF
- Page 1: Risk level (EXTREME), top 5 actions, supply checklist, emergency contacts
- Page 2: Shelter locations map, budget breakdown ($50), QR codes for resources
- Format: Black & white friendly, print-optimized
- Download: Successful PDF generation in under 10 seconds

### Expected Output

**Plan Completion Time**: 120-180 seconds
**Agent Success Rate**: 7/7 agents complete successfully
**PDF Size**: Under 2 MB
**Mobile Display**: All content readable on 375px width (iPhone SE)

### Pass/Fail Criteria
✅ **Pass if**:
- Risk level correctly identified as EXTREME
- Supply list totals $48-50 (within budget)
- Budget warning shown to user
- At least 8 resources located in Miami area
- 5 videos curated (all under 5 min)
- PDF downloads successfully
- Total time under 180 seconds

❌ **Fail if**:
- Supply list exceeds $50
- No budget warning shown despite EXTREME risk
- Fewer than 5 resources found
- Any agent returns error
- Time exceeds 180 seconds
- PDF generation fails

---

## Scenario 2: Moderate Natural Disaster, High Budget
**Test ID**: TS-002
**Priority**: P1
**User Story**: US1 (Natural Disaster Preparedness Plan)

### Input Profile
- **Crisis Mode**: Natural Disaster
- **Specific Threat**: Earthquake
- **Location**: San Francisco, CA 94102 (known earthquake zone)
- **Household**: 2 adults, 1 child, 1 dog
- **Housing Type**: House
- **Budget Tier**: $200+ (highest)
- **Timing**: Year-round (earthquake risk is constant)

### Expected Agent Behavior

**Risk Assessment Agent**:
- Risk Level: HIGH (not EXTREME - earthquakes less predictable than hurricanes)
- Severity Score: 75-85
- Threat: "Major earthquake (6.5+) overdue on San Andreas Fault"
- Historical data: References 1989 Loma Prieta earthquake, 1906 SF quake
- Timeline: "No specific timing, but preparedness critical"

**Supply Planning Agent**:
- Tier: All three tiers (Critical + Prepared + Comprehensive)
- Items: Includes generator, extended food supply (14 days), pet supplies (dog food, leash, bowl), specialty gear (earthquake safety kit, gas shut-off wrench)
- Household scaling: Quantities for 3 people + 1 pet
- Total cost: $195-205 (acceptable slight overage for Comprehensive tier)
- Recommendations: "Secure heavy furniture, identify safe spots (doorways, sturdy tables)"

**Resource Locator Agent**:
- Find: Emergency shelters in SF (note which allow pets)
- Find: Pet-friendly resources (emergency vet, pet supply stores)
- Find: Hardware stores (Home Depot, Lowe's for safety equipment)
- Find: Community meeting points (Golden Gate Park, civic centers)
- Distance: Within 15-mile radius

**Video Curator Agent**:
- Return: 5-7 earthquake prep videos
- Topics: "Earthquake-proof your home", "What to do during an earthquake", "Preparing pets for disasters", "Aftershock safety"
- Pet-specific: At least 1 video on pet safety

**Documentation Agent**:
- Generate: 2-page PDF with pet considerations
- Include: Pet emergency plan (food, meds, vet records, photo for lost pet posters)
- Include: QR code linking to pet-friendly shelters

### Expected Output

**Plan Completion Time**: 100-150 seconds (faster than Scenario 1 due to less urgency)
**Agent Success Rate**: 7/7 agents complete successfully
**Pet Accommodations**: Pet supplies included, pet-friendly shelters noted

### Pass/Fail Criteria
✅ **Pass if**:
- Risk level HIGH (not EXTREME)
- Supply list includes pet-specific items
- At least 2 pet-friendly shelters found
- At least 1 pet safety video included
- Total cost $195-210 acceptable
- Earthquake-specific guidance (furniture securing, aftershock planning)

❌ **Fail if**:
- Pet supplies missing
- No pet-friendly shelters identified
- Supply list under $150 (not using full budget potential)
- Generic disaster plan (not earthquake-specific)

---

## Scenario 3: Economic Crisis, Single Adult, Minimal Savings
**Test ID**: TS-003
**Priority**: P0 (Blocker)
**User Story**: US2 (Economic Crisis Survival Plan)

### Input Profile
- **Crisis Mode**: Economic Crisis
- **Specific Threat**: Unemployment (sudden job loss)
- **Location**: Austin, TX 78701
- **Household**: 1 adult, 0 children, 0 pets
- **Housing Type**: Apartment
- **Budget Tier**: $50
- **Runtime Questions**:
  - "What worries you most?" → "Eviction or foreclosure"
  - "How long can you cover essentials?" → "Less than 2 weeks"
  - "Top priority?" → "Keep my housing"
  - "Any income?" → "No"

### Expected Agent Behavior

**Risk Assessment Agent (Economic Mode)**:
- UI Label: "💰 Financial Risk Agent"
- Risk Level: EXTREME
- Severity Score: 95-100
- Analysis: "Critical financial risk - Less than 2 weeks runway with $0 income and housing at risk"
- Context: Uses user's runtime responses to assess urgency

**Planning Agent (Economic Mode)**:
- UI Label: "📊 Budget Planning Agent"
- Focus: Survival for 30-90 days on $50
- Priority 1: Housing preservation (rent assistance programs, landlord hardship letter)
- Priority 2: Food security (SNAP application, food banks)
- Priority 3: Income generation (unemployment filing, gig work, temp agencies)
- Supply list: Minimal food stockpiling within $50 (rice, beans, pasta, canned goods for 30 days)

**Financial Advisor Agent**:
- Expense categorization:
  - Must-Pay: Rent (top priority per user input)
  - Defer: Credit cards, subscriptions
  - Eliminate: Entertainment, dining out, non-essentials
- Action timeline:
  - Day 1: Contact landlord, explain situation, request payment plan
  - Day 2: Apply for unemployment benefits
  - Day 3: Apply for SNAP (food stamps)
  - Day 5: Visit food banks, pick up emergency supplies
  - Day 7: Apply for emergency rental assistance (local/state programs)
  - Day 10: Start gig work applications (Uber, DoorDash, TaskRabbit)
  - Day 14: Follow up on unemployment claim

**Resource Locator Agent**:
- Find: Unemployment office (Texas Workforce Commission - Austin location)
- Find: Food banks (Capital Area Food Bank, local church pantries)
- Find: Free clinics (CommUnityCare, People's Community Clinic)
- Find: Job centers (Austin Public Library employment resources)
- Find: Emergency rental assistance (ECHO - Ending Community Homelessness Coalition)
- Distance: All within Austin metro area

**Video Curator Agent**:
- Return: 5 videos
- Topics: "How to file unemployment in Texas", "SNAP benefits explained", "Negotiating with landlord", "Fast cash jobs", "Surviving financial crisis"
- Sources: Department of Labor, financial advisors, personal finance YouTubers

**Documentation Agent**:
- Generate: 2-page PDF
- Page 1: Financial risk level, immediate actions (1-14 days), landlord hardship letter template
- Page 2: Food bank locations, unemployment office address, SNAP application QR code, gig work platforms list

### Expected Output

**Plan Completion Time**: 90-120 seconds
**Agent Success Rate**: 7/7 agents complete successfully
**Actionable Steps**: At least 10 specific action items with deadlines

### Pass/Fail Criteria
✅ **Pass if**:
- Risk level EXTREME (correctly assesses 2-week runway as critical)
- Housing preservation is top priority (matches user input)
- At least 5 food banks located in Austin
- Hardship letter template included
- Unemployment filing guidance specific to Texas
- At least 10 action items with specific days/deadlines

❌ **Fail if**:
- Risk level anything other than EXTREME
- Advice doesn't prioritize housing (user's stated concern)
- Generic advice not specific to Texas unemployment system
- Fewer than 3 food banks found
- No hardship letter template

---

## Scenario 4: Economic Crisis, Family of 4, Dual Income Loss, Moderate Savings
**Test ID**: TS-004
**Priority**: P1
**User Story**: US2 (Economic Crisis Survival Plan) + US6 (Strategic Crisis Planning)

### Input Profile
- **Crisis Mode**: Economic Crisis
- **Specific Threat**: Government Shutdown (federal employees)
- **Location**: Washington, DC 20001
- **Household**: 2 adults, 2 children (ages 8, 12)
- **Housing Type**: House
- **Budget Tier**: $100
- **Runtime Questions**:
  - "What worries you most?" → "Can't afford food"
  - "How long can you cover essentials?" → "1-3 months"
  - "Top priority?" → "Feed my family"
  - "Any income?" → "Yes, $500-1500" (partial unemployment or spouse's reduced hours)
- **Strategic Planning**: ENABLED (user opts in for expanded guidance)

### Expected Agent Behavior

**Risk Assessment Agent**:
- Risk Level: MEDIUM-HIGH
- Severity Score: 60-70
- Analysis: "Moderate financial risk - 1-3 month runway with partial income, 4-person household increases expenses"
- Context: Less dire than Scenario 3 due to savings buffer and partial income

**Planning Agent**:
- Focus: Food security for family of 4
- Priority 1: SNAP application (4-person household likely qualifies even with $500-1500/mo income)
- Priority 2: School meal programs (kids ages 8, 12 → free/reduced lunch)
- Priority 3: Food stockpiling within $100 budget (bulk rice, beans, pasta, canned goods, peanut butter)
- Household scaling: Quantities for 4 people, 30-day supply
- Total cost: $95-100

**Financial Advisor Agent (Strategic Planning Mode)**:
- Expanded guidance:
  - Unemployment benefits: Estimate for DC federal worker (~$400-600/week)
  - SNAP benefits: Estimate for 4-person household in DC (~$600-800/month)
  - Bill prioritization: Mortgage/rent, utilities, food, defer credit cards
  - Hardship letters: Templates for mortgage company, credit cards, utilities
  - Job resources: Federal resume tips, USAJobs.gov, contracting companies hiring ex-fed employees
  - Income strategies: Spouse increasing hours, temporary work during shutdown

**Resource Locator Agent**:
- Find: Food banks in DC (Capital Area Food Bank, Martha's Table)
- Find: Schools with meal programs (DC Public Schools - identify nearest 2 schools)
- Find: Unemployment office (DC Department of Employment Services)
- Find: Free family activities (libraries, parks - to reduce entertainment costs)
- Find: Emergency assistance programs (DC Emergency Rental Assistance Program)

**Video Curator Agent**:
- Return: 5 videos
- Topics: "Feeding family on $100/month", "Government shutdown survival guide", "SNAP application walkthrough", "Helping kids understand financial crisis", "DC food resources"

**Documentation Agent**:
- Generate: 2-page core + 2-page Strategic Planning appendix (4 pages total)
- Core Pages:
  - Page 1: Risk level, immediate actions, food supply checklist
  - Page 2: Food banks, SNAP office, school meal programs
- Strategic Planning Appendix:
  - Page 3: Unemployment filing guide, benefits estimates, income sources analysis
  - Page 4: Hardship letter templates, job search resources, family budget worksheet

### Expected Output

**Plan Completion Time**: 150-180 seconds (longer due to Strategic Planning)
**Agent Success Rate**: 7/7 agents complete successfully
**Strategic Planning Depth**: 15+ action items across short-term (survival) and long-term (recovery)

### Pass/Fail Criteria
✅ **Pass if**:
- Risk level MEDIUM-HIGH (not EXTREME due to savings buffer)
- Food security prioritized (matches user input)
- SNAP and school meal programs prominently featured
- Strategic Planning appendix includes unemployment filing, job resources, hardship letters
- At least 3 food banks in DC area
- Family-specific guidance (kids mentioned, 4-person quantities)

❌ **Fail if**:
- Risk level EXTREME (should recognize savings buffer lowers urgency)
- Strategic Planning expansion not generated
- Food quantities not scaled for 4 people
- No mention of school meal programs (kids ages 8, 12)

---

## Scenario 5: Edge Case - Rural Location, Limited Resources, Extreme Wildfire Risk
**Test ID**: TS-005
**Priority**: P2
**User Story**: US1 (Natural Disaster Preparedness Plan) + Edge Cases

### Input Profile
- **Crisis Mode**: Natural Disaster
- **Specific Threat**: Wildfire
- **Location**: Paradise, CA 95969 (site of 2018 Camp Fire, rural)
- **Household**: 1 adult, 1 elderly parent (mobility issues), 1 pet (cat)
- **Housing Type**: Mobile home
- **Budget Tier**: $100
- **Special Considerations**: Elderly parent with limited mobility, rural area with sparse resources

### Expected Agent Behavior

**Risk Assessment Agent**:
- Risk Level: EXTREME
- Severity Score: 95-100
- Threat: "Extreme wildfire risk - Paradise destroyed by Camp Fire in 2018, high-risk zone"
- Historical data: References Camp Fire (85 deaths, town evacuated)
- Timeline: "Fire season June-November, evacuation may be required with minimal notice"
- Special notes: "Mobile home offers limited protection, evacuation plan critical"

**Supply Planning Agent**:
- Focus: Evacuation readiness (wildfires require leaving, not sheltering in place)
- Items: Go-bags (2 people + cat), N95 masks (smoke), flashlights, batteries, phone chargers, important documents in waterproof bag, 3 days portable food/water
- Special considerations: Mobility aids for elderly parent (wheelchair, walker), cat carrier and pet supplies
- Total cost: $98-105
- Recommendations: "Pre-pack car with essentials, keep gas tank full, plan evacuation route NOW"

**Financial Advisor Agent**:
- Quick assessment: "Do you have funds for hotel evacuation?"
- Suggests: Red Cross shelters (free), FEMA assistance post-disaster, insurance claim preparation

**Resource Locator Agent** (CRITICAL TEST):
- Challenge: Rural area, limited nearby resources
- Find: Emergency shelters (likely NONE in Paradise - town too small)
- Expand search: Chico, CA (20 miles away) - find 3-5 Red Cross shelters
- Find: Evacuation routes (Highway 99 South to Chico, avoid Paradise Park during fire)
- Find: Pet-friendly shelters or vet clinics in Chico
- Find: Supply stores (Walmart in Chico, CVS Pharmacy)
- Data source: Static database likely insufficient, Google Places API fallback required
- Distance: Most resources 20-50 miles (note transportation challenge)
- **Special note displayed**: "Limited resources in your immediate area. Nearest shelters are 20 miles away in Chico. Ensure reliable transportation."

**Video Curator Agent**:
- Return: 5 videos
- Topics: "Wildfire evacuation checklist", "Evacuating with elderly family", "Pet evacuation tips", "Camp Fire survivor stories", "Fire safety for mobile homes"
- Tone: Urgent, evacuation-focused (not shelter-in-place)

**Documentation Agent**:
- Generate: 2-page PDF
- Page 1: EXTREME risk warning, evacuation checklist, go-bag contents, important documents list
- Page 2: Evacuation routes map (Paradise to Chico), pet-friendly shelters in Chico, emergency contacts, mobility considerations for elderly parent

### Expected Output

**Plan Completion Time**: 140-180 seconds (longer due to expanded resource search radius)
**Agent Success Rate**: 7/7 agents complete successfully (even with limited local resources)
**Resource Radius**: Successfully expands search to 50-mile radius

### Pass/Fail Criteria
✅ **Pass if**:
- Risk level EXTREME (correctly assesses wildfire + mobile home + rural = highest risk)
- Evacuation-focused plan (not shelter-in-place)
- Resources found in Chico (20-50 miles away)
- Clear note: "Limited local resources, nearest help in Chico"
- Elderly mobility considerations mentioned
- Pet supplies and pet-friendly shelters included
- Evacuation routes clearly mapped

❌ **Fail if**:
- Shelter-in-place advice given (wrong for wildfire + mobile home)
- Resource Locator returns "no results" (should expand radius)
- No mention of mobility challenges
- Pet needs ignored
- Evacuation routes not provided

---

## Test Execution Plan

### Pre-Hackathon Testing (Before Oct 31)
1. **Manual Testing**: Run all 5 scenarios manually, document results
2. **Automated E2E Tests**: Write Playwright tests for Scenarios 1, 3 (P0 blockers)
3. **Performance Testing**: Verify all scenarios complete under 180 seconds
4. **Mobile Testing**: Test Scenario 1 on iPhone SE viewport (320px width)
5. **PDF Testing**: Download and verify PDFs from each scenario

### During Hackathon Demo
- **Primary Demo**: Scenario 1 (Hurricane, Miami, $50 budget) - most dramatic
- **Backup Demo**: Scenario 3 (Unemployment, Austin, minimal savings) - shows economic crisis mode
- **Judges' Live Test**: Offer to run scenario with their own location/crisis type

### Post-Hackathon Validation
- **User Testing**: Share with bootcamp cohort, collect feedback
- **Edge Case Expansion**: Add 10+ more edge case scenarios
- **Regression Suite**: Automate all 5 scenarios as CI/CD checks

---

## Success Metrics

### Overall MVP Success
✅ **MVP is demo-ready if**:
- Scenarios 1 and 3 pass 100% (P0 blockers)
- Scenarios 2, 4, 5 pass at least 80% (P1/P2)
- All scenarios complete under 180 seconds
- PDFs download successfully in all cases
- Mobile display works for Scenario 1

❌ **MVP needs more work if**:
- Any P0 scenario fails
- Completion time exceeds 180 seconds for any scenario
- PDF generation fails in more than 1 scenario
- Resource Locator returns zero results for any location

---

**Version**: 1.0 | **Status**: Approved | **Last Updated**: 2025-10-28
