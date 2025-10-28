"""Documentation Agent for assembling complete crisis plan and generating PDF.

Generates simplified 2-page PDF (MVP):
- Page 1: Crisis Overview & Action Plan
- Page 2: Resources & Budget

Uses ReportLab for PDF generation with print-optimized layout.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from .base_agent import BaseAgent
from ..models.blackboard import Blackboard
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentationAgent(BaseAgent):
    """Agent that assembles complete crisis plan and generates PDF.

    Final agent in the orchestration chain:
    - Reads all agent results from blackboard
    - Assembles complete plan
    - Generates 2-page PDF
    - Handles partial plans gracefully (if agents failed)
    """

    def __init__(self, claude_client, timeout: int = 30):
        """Initialize Documentation Agent."""
        super().__init__(claude_client, timeout)
        self.agent_type = "documentation"

    async def process(self, blackboard: Blackboard) -> Blackboard:
        """
        Assemble complete plan and generate PDF using blackboard pattern.

        Reads from blackboard:
        - crisis_profile
        - risk_assessment
        - supply_plan
        - economic_plan (if economic crisis)
        - resource_locations
        - video_recommendations

        Writes to blackboard:
        - complete_plan (assembled plan data)
        - pdf_path (file path to generated PDF)

        Args:
            blackboard: Shared blackboard state

        Returns:
            Updated blackboard with complete_plan and pdf_path
        """
        self.start_time = datetime.utcnow()
        crisis_profile = blackboard.crisis_profile

        if not crisis_profile:
            raise ValueError("Blackboard missing crisis_profile")

        task_id = crisis_profile.get('task_id', 'unknown')
        crisis_mode = crisis_profile.get('crisis_mode')

        # Get mode-specific UI presentation
        agent_label = self.get_agent_label(crisis_mode)
        agent_emoji = self.get_agent_emoji(crisis_mode)

        logger.info(f"{agent_emoji} {agent_label} starting for task_id={task_id}, mode={crisis_mode}")

        try:
            # Assemble complete plan from all agent results
            complete_plan = self._assemble_complete_plan(blackboard)

            logger.info(f"{agent_emoji} Complete plan assembled, generating PDF...")

            # Generate PDF
            pdf_path = self._generate_pdf(blackboard, complete_plan)

            logger.info(f"{agent_emoji} PDF generated: {pdf_path}")

            # Write to blackboard
            blackboard.complete_plan = complete_plan
            blackboard.pdf_path = pdf_path

            # No tokens used (no Claude API call for PDF generation)
            self.tokens_used = 0
            self.cost = 0.0

            blackboard.mark_agent_complete(
                self.agent_class_name,
                self.tokens_used,
                self.cost
            )

            self.end_time = datetime.utcnow()
            logger.info(
                f"{agent_emoji} {agent_label} completed: "
                f"PDF generated at {pdf_path}"
            )

            return blackboard

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"{agent_emoji} {agent_label} error: {e}")
            raise

    def _assemble_complete_plan(self, blackboard: Blackboard) -> Dict[str, Any]:
        """Assemble complete plan from all agent results."""
        crisis_profile = blackboard.crisis_profile
        crisis_mode = crisis_profile.get('crisis_mode')

        complete_plan = {
            "task_id": crisis_profile.get('task_id'),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "crisis_mode": crisis_mode,
            "crisis_type": crisis_profile.get('specific_threat'),
            "location": crisis_profile.get('location'),
            "household": crisis_profile.get('household'),
            "budget_tier": crisis_profile.get('budget_tier'),
        }

        # Include agent results (with graceful handling of missing data)
        if blackboard.risk_assessment:
            complete_plan["risk_assessment"] = blackboard.risk_assessment
        else:
            logger.warning("⚠️ Risk assessment missing from blackboard")
            complete_plan["risk_assessment"] = None

        if blackboard.supply_plan:
            complete_plan["supply_plan"] = blackboard.supply_plan
        else:
            logger.warning("⚠️ Supply plan missing from blackboard")
            complete_plan["supply_plan"] = None

        # Economic plan (only for economic crisis)
        if crisis_mode == "economic_crisis" and blackboard.economic_plan:
            complete_plan["economic_plan"] = blackboard.economic_plan
        else:
            complete_plan["economic_plan"] = None

        # Resource locations
        complete_plan["resource_locations"] = blackboard.resource_locations or []

        # Video recommendations
        complete_plan["video_recommendations"] = blackboard.video_recommendations or []

        # Status tracking
        complete_plan["agents_completed"] = blackboard.agents_completed
        complete_plan["agents_failed"] = blackboard.agents_failed
        complete_plan["total_execution_seconds"] = blackboard.total_execution_seconds
        complete_plan["total_tokens_used"] = blackboard.total_tokens_used
        complete_plan["total_cost_estimate"] = blackboard.total_cost_estimate

        return complete_plan

    def _generate_pdf(self, blackboard: Blackboard, complete_plan: Dict[str, Any]) -> str:
        """
        Generate 2-page PDF using ReportLab.

        Page 1: Crisis Overview & Action Plan
        Page 2: Resources & Budget

        Args:
            blackboard: Blackboard state
            complete_plan: Assembled plan data

        Returns:
            File path to generated PDF
        """
        task_id = complete_plan.get('task_id', 'unknown')
        crisis_mode = complete_plan.get('crisis_mode')
        crisis_type = complete_plan.get('crisis_type', 'Unknown')

        # Create output directory if it doesn't exist
        output_dir = Path("output/pdfs")
        output_dir.mkdir(parents=True, exist_ok=True)

        # PDF filename
        pdf_filename = f"crisis_plan_{task_id}.pdf"
        pdf_path = output_dir / pdf_filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )

        # Build content
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=12,
            alignment=TA_CENTER,
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=6,
            spaceBefore=12,
        )

        # PAGE 1: Crisis Overview & Action Plan
        story.append(Paragraph("PrepSmart Crisis Preparedness Plan", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Crisis Overview
        location = complete_plan.get('location', {})
        household = complete_plan.get('household', {})

        overview_text = f"""
        <b>Crisis Type:</b> {crisis_type.replace('_', ' ').title()}<br/>
        <b>Location:</b> {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}<br/>
        <b>Household:</b> {household.get('adults', 0)} adults, {household.get('children', 0)} children<br/>
        <b>Budget Tier:</b> ${complete_plan.get('budget_tier', 0)}<br/>
        <b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        """
        story.append(Paragraph(overview_text, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Risk Assessment
        risk_assessment = complete_plan.get('risk_assessment')
        if risk_assessment:
            story.append(Paragraph("Risk Assessment", heading_style))
            risk_level = risk_assessment.get('overall_risk_level', 'UNKNOWN')
            risk_color = self._get_risk_color(risk_level)

            risk_text = f"""
            <b>Risk Level:</b> <font color="{risk_color}">{risk_level}</font><br/>
            <b>Severity Score:</b> {risk_assessment.get('severity_score', 'N/A')}/100
            """
            story.append(Paragraph(risk_text, styles['Normal']))

            # Top recommendations
            recommendations = risk_assessment.get('recommendations', [])[:5]
            if recommendations:
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("<b>Top 5 Immediate Actions:</b>", styles['Normal']))
                for i, rec in enumerate(recommendations, 1):
                    story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        else:
            story.append(Paragraph("Risk Assessment: <i>Data unavailable</i>", heading_style))

        story.append(Spacer(1, 0.2 * inch))

        # Supply Plan (condensed)
        supply_plan = complete_plan.get('supply_plan')
        if supply_plan:
            story.append(Paragraph("Supply Checklist (Critical Items)", heading_style))

            tiers = supply_plan.get('tiers', {})
            critical_tier = tiers.get('critical', {})
            items = critical_tier.get('items', [])[:10]  # Limit to 10 items

            if items:
                # Create table
                table_data = [['Item', 'Quantity', 'Est. Price']]
                for item in items:
                    table_data.append([
                        item.get('name', ''),
                        f"{item.get('quantity', '')} {item.get('unit', '')}",
                        f"${item.get('estimated_price', 0):.2f}"
                    ])

                supply_table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1*inch])
                supply_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(supply_table)

                total_cost = critical_tier.get('total_cost', 0)
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(f"<b>Total Critical Supplies:</b> ${total_cost:.2f}", styles['Normal']))
        else:
            story.append(Paragraph("Supply Checklist: <i>Data unavailable</i>", heading_style))

        # PAGE BREAK
        story.append(PageBreak())

        # PAGE 2: Resources & Budget
        story.append(Paragraph("Local Resources & Budget", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Resource Locations
        resource_locations = complete_plan.get('resource_locations', [])
        if resource_locations:
            story.append(Paragraph("Nearby Assistance Resources", heading_style))

            # Limit to top 8 resources
            top_resources = resource_locations[:8]

            for resource in top_resources:
                resource_text = f"""
                <b>{resource.get('name', '')}</b> ({resource.get('resource_type', '').replace('_', ' ').title()})<br/>
                {resource.get('address', '')}, {resource.get('city', '')}, {resource.get('state', '')}<br/>
                Phone: {resource.get('phone', 'N/A')} | Distance: {resource.get('distance_miles', 'N/A')} mi
                """
                story.append(Paragraph(resource_text, styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph("Local Resources: <i>Data unavailable</i>", heading_style))

        story.append(Spacer(1, 0.2 * inch))

        # Economic Plan (if applicable)
        economic_plan = complete_plan.get('economic_plan')
        if crisis_mode == "economic_crisis" and economic_plan:
            story.append(Paragraph("30-Day Financial Survival Strategy", heading_style))

            financial_summary = economic_plan.get('financial_summary', {})
            survival_outlook = economic_plan.get('survival_outlook', {})

            econ_text = f"""
            <b>Available Savings:</b> ${financial_summary.get('available_savings', 0)}<br/>
            <b>Monthly Expenses (Revised):</b> ${economic_plan.get('revised_monthly_expenses', 0)}<br/>
            <b>Estimated Relief:</b> {economic_plan.get('estimated_total_relief', 'N/A')}<br/>
            <b>Survival Outlook:</b> {survival_outlook.get('with_action', 'N/A')}
            """
            story.append(Paragraph(econ_text, styles['Normal']))

        # Video Resources
        video_recommendations = complete_plan.get('video_recommendations', [])
        if video_recommendations:
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("Educational Videos", heading_style))

            for video in video_recommendations[:5]:  # Limit to 5
                video_text = f"""
                • <b>{video.get('title', '')}</b> ({video.get('duration_formatted', '')})<br/>
                  Source: {video.get('source', '')} | {video.get('url', '')}
                """
                story.append(Paragraph(video_text, styles['Normal']))

        # Footer
        story.append(Spacer(1, 0.3 * inch))
        footer_text = """
        <i>Generated by PrepSmart - Multi-Agent AI Crisis Preparedness Assistant</i><br/>
        <i>Always verify information with local authorities. This plan is for guidance only.</i>
        """
        story.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )))

        # Build PDF
        doc.build(story)

        return str(pdf_path)

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color code for risk level."""
        risk_colors = {
            "LOW": "#48bb78",       # Green
            "MEDIUM": "#ed8936",    # Orange
            "HIGH": "#f56565",      # Red
            "EXTREME": "#c53030",   # Dark Red
        }
        return risk_colors.get(risk_level, "#718096")  # Default gray
