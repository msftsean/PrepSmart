# PrepSmart Frontend

**Mobile-first vanilla JavaScript implementation**

## Structure

```
frontend/
├── index.html                      # Landing page with hero and crisis mode selection
├── pages/
│   ├── crisis-select.html          # Specific disaster/crisis type selection
│   ├── questionnaire.html          # Multi-step form (4 steps)
│   ├── agent-progress.html         # Real-time agent dashboard
│   └── plan-results.html           # Complete plan display with PDF download
├── assets/
│   ├── css/
│   │   ├── main.css                # Core styles and design system
│   │   └── mobile.css              # Responsive styles (320px-1280px)
│   └── js/
│       ├── api-client.js           # Backend API wrapper
│       ├── form-handler.js         # Multi-step form logic
│       └── agent-dashboard.js      # Real-time status polling
└── README.md
```

## Features

### Design System
- **Colors**: Primary (#1E40AF), Danger (#DC2626), Success (#16A34A)
- **Typography**: System font stack, 16px minimum
- **Touch Targets**: 44px minimum (mobile-friendly)
- **Accessibility**: WCAG 2.1 AA compliant, keyboard navigation, screen reader support

### Pages

#### 1. Landing Page ([index.html](index.html))
- Hero section with crisis mode selection
- Features grid
- How it works section
- Mobile-responsive cards

#### 2. Crisis Selection ([pages/crisis-select.html](pages/crisis-select.html))
- **Natural Disaster**: 6 disaster types (hurricane, earthquake, wildfire, flood, tornado, blizzard)
- **Economic Crisis**: Crisis type dropdown with optional description
- Visual card selection with icons

#### 3. Questionnaire ([pages/questionnaire.html](pages/questionnaire.html))
4-step form with progress indicator:
- **Step 1**: Location (ZIP, city, state)
- **Step 2**: Household (adults, children, pets, housing type)
- **Step 3**: Budget (natural) or Financial situation (economic)
- **Step 4**: Review and submit

Features:
- Form validation
- sessionStorage persistence
- Mobile-optimized inputs
- Progress tracking

#### 4. Agent Progress ([pages/agent-progress.html](pages/agent-progress.html))
Real-time agent dashboard:
- Overall progress bar
- 6 agent status cards with icons
- Live log streaming
- Time estimate countdown
- Auto-redirect to results when complete

#### 5. Plan Results ([pages/plan-results.html](pages/plan-results.html))
Complete plan display:
- Collapsible sections
- Risk assessment with color-coded severity
- Supply checklist with checkboxes
- Economic plan with action items
- Resource locations
- Video recommendations
- PDF download button
- Print-friendly layout

## API Integration

### Endpoints Used

```javascript
// Start plan generation
POST /api/crisis/start
→ Returns: { task_id: string }

// Poll for status
GET /api/crisis/{task_id}/status
→ Returns: { status, progress, agent_statuses }

// Get complete result
GET /api/crisis/{task_id}/result
→ Returns: { risk_assessment, supply_plan, economic_plan, ... }

// Download PDF
GET /api/crisis/{task_id}/pdf
→ Returns: PDF blob
```

### Flow

1. User fills questionnaire → POST /api/crisis/start
2. Redirect to agent-progress.html with task_id
3. Poll GET /api/crisis/{task_id}/status every 2 seconds
4. When complete, redirect to plan-results.html
5. GET /api/crisis/{task_id}/result to display plan
6. GET /api/crisis/{task_id}/pdf for download

## Running Locally

### Option 1: Python HTTP Server

```bash
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```

### Option 2: Node HTTP Server

```bash
cd frontend
npx http-server -p 8000
# Visit http://localhost:8000
```

### Backend Connection

Frontend expects backend at:
- **Development**: `http://localhost:5000/api`
- **Production**: `/api` (same origin)

Configure in [assets/js/api-client.js](assets/js/api-client.js):

```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:5000/api'
  : '/api';
```

## Mobile Testing

### Viewports Tested
- iPhone SE: 320px
- iPhone 12/13: 390px
- iPhone Pro Max: 428px
- iPad: 768px
- Desktop: 1280px+

### Testing Tools
- Chrome DevTools Device Mode
- Firefox Responsive Design Mode
- Real device testing (iOS/Android)

### Performance
- Target: <3s load time on 3G
- No external dependencies (jQuery, Bootstrap, etc.)
- Inline critical CSS for above-the-fold content

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility Features

- Semantic HTML
- ARIA labels where needed
- Keyboard navigation
- Focus indicators
- Skip to main content link
- High contrast mode support
- Reduced motion support
- Screen reader compatibility

## Future Enhancements

- [ ] Service Worker for offline support
- [ ] Dark mode toggle
- [ ] Multi-language support (i18n)
- [ ] Progressive Web App (PWA) capabilities
- [ ] Server-Sent Events (SSE) for live logs
- [ ] Share plan via link
- [ ] Save plan to user account

## License

MIT
