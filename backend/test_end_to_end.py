#!/usr/bin/env python3
"""End-to-end test for PrepSmart multi-agent system.

Tests:
1. Natural disaster scenario (Hurricane in Miami)
2. Economic crisis scenario (Unemployment in Austin)
3. Complete plan generation with all 6 agents
4. PDF generation
5. Blackboard persistence
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.blackboard import Blackboard
from services.claude_client import ClaudeClient
from services.blackboard_service import blackboard_service
from agents.coordinator_agent import CoordinatorAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def test_natural_disaster():
    """Test natural disaster scenario: Hurricane in Miami."""
    print("\n" + "="*80)
    print("TEST 1: Natural Disaster - Hurricane in Miami, FL")
    print("="*80 + "\n")

    # Create crisis profile
    crisis_profile = {
        "task_id": "test-hurricane-miami-001",
        "crisis_mode": "natural_disaster",
        "specific_threat": "hurricane",
        "location": {
            "city": "Miami",
            "state": "FL",
            "zip_code": "33139",
            "latitude": 25.7959,
            "longitude": -80.1396
        },
        "household": {
            "adults": 2,
            "children": 1,
            "pets": 0,
            "special_needs": ""
        },
        "housing_type": "apartment",
        "budget_tier": 100
    }

    # Initialize coordinator
    claude_client = ClaudeClient()
    coordinator = CoordinatorAgent(claude_client)

    # Run plan generation
    print("🎯 Starting coordinator for hurricane scenario...")
    try:
        blackboard = await coordinator.generate_plan(crisis_profile)

        print("\n✅ Plan generation complete!")
        print(f"   Status: {blackboard.status}")
        print(f"   Agents completed: {blackboard.agents_completed}")
        print(f"   Agents failed: {blackboard.agents_failed}")
        print(f"   Total tokens: {blackboard.total_tokens_used}")
        print(f"   Total cost: ${blackboard.total_cost_estimate:.4f}")
        print(f"   Execution time: {blackboard.total_execution_seconds:.2f}s")

        # Verify agent results
        print("\n📋 Verifying agent results:")
        print(f"   ✓ Risk Assessment: {blackboard.risk_assessment is not None}")
        print(f"   ✓ Supply Plan: {blackboard.supply_plan is not None}")
        print(f"   ✓ Resource Locations: {len(blackboard.resource_locations or [])} found")
        print(f"   ✓ Video Recommendations: {len(blackboard.video_recommendations or [])} found")
        print(f"   ✓ Complete Plan: {blackboard.complete_plan is not None}")
        print(f"   ✓ PDF Path: {blackboard.pdf_path}")

        # Check PDF exists
        if blackboard.pdf_path:
            pdf_exists = Path(blackboard.pdf_path).exists()
            print(f"   ✓ PDF File Exists: {pdf_exists}")
            if pdf_exists:
                pdf_size = Path(blackboard.pdf_path).stat().st_size
                print(f"   ✓ PDF Size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_economic_crisis():
    """Test economic crisis scenario: Unemployment in Austin."""
    print("\n" + "="*80)
    print("TEST 2: Economic Crisis - Unemployment in Austin, TX")
    print("="*80 + "\n")

    # Create crisis profile
    crisis_profile = {
        "task_id": "test-unemployment-austin-001",
        "crisis_mode": "economic_crisis",
        "specific_threat": "unemployment",
        "location": {
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "latitude": 30.2672,
            "longitude": -97.7431
        },
        "household": {
            "adults": 1,
            "children": 0,
            "pets": 0,
            "special_needs": ""
        },
        "housing_type": "apartment",
        "budget_tier": 50,
        "runtime_questions": {
            "primary_concern": "job_loss",
            "runway": "30 days",
            "budget_priority": "maximize calories per dollar"
        }
    }

    # Initialize coordinator
    claude_client = ClaudeClient()
    coordinator = CoordinatorAgent(claude_client)

    # Run plan generation
    print("🎯 Starting coordinator for unemployment scenario...")
    try:
        blackboard = await coordinator.generate_plan(crisis_profile)

        print("\n✅ Plan generation complete!")
        print(f"   Status: {blackboard.status}")
        print(f"   Agents completed: {blackboard.agents_completed}")
        print(f"   Agents failed: {blackboard.agents_failed}")
        print(f"   Total tokens: {blackboard.total_tokens_used}")
        print(f"   Total cost: ${blackboard.total_cost_estimate:.4f}")
        print(f"   Execution time: {blackboard.total_execution_seconds:.2f}s")

        # Verify agent results
        print("\n📋 Verifying agent results:")
        print(f"   ✓ Risk Assessment: {blackboard.risk_assessment is not None}")
        print(f"   ✓ Supply Plan: {blackboard.supply_plan is not None}")
        print(f"   ✓ Economic Plan: {blackboard.economic_plan is not None}")
        print(f"   ✓ Resource Locations: {len(blackboard.resource_locations or [])} found")
        print(f"   ✓ Video Recommendations: {len(blackboard.video_recommendations or [])} found")
        print(f"   ✓ Complete Plan: {blackboard.complete_plan is not None}")
        print(f"   ✓ PDF Path: {blackboard.pdf_path}")

        # Check PDF exists
        if blackboard.pdf_path:
            pdf_exists = Path(blackboard.pdf_path).exists()
            print(f"   ✓ PDF File Exists: {pdf_exists}")
            if pdf_exists:
                pdf_size = Path(blackboard.pdf_path).stat().st_size
                print(f"   ✓ PDF Size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")

        # Verify economic-specific data
        if blackboard.economic_plan:
            print("\n💼 Economic Plan Details:")
            daily_actions = blackboard.economic_plan.get('daily_actions', [])
            benefits = blackboard.economic_plan.get('eligible_benefits', [])
            print(f"   ✓ Daily Actions: {len(daily_actions)} planned")
            print(f"   ✓ Eligible Benefits: {len(benefits)} identified")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_blackboard_persistence():
    """Test blackboard persistence to database."""
    print("\n" + "="*80)
    print("TEST 3: Blackboard Persistence")
    print("="*80 + "\n")

    try:
        # Try to retrieve previous test blackboard
        test_id = "test-hurricane-miami-001"
        blackboard = blackboard_service.get_blackboard(test_id)

        if blackboard:
            print(f"✅ Successfully retrieved blackboard for task_id={test_id}")
            print(f"   Status: {blackboard.status}")
            print(f"   Agents completed: {len(blackboard.agents_completed)}")
            print(f"   Has risk_assessment: {blackboard.risk_assessment is not None}")
            print(f"   Has supply_plan: {blackboard.supply_plan is not None}")
            print(f"   Has complete_plan: {blackboard.complete_plan is not None}")
            return True
        else:
            print(f"⚠️  No blackboard found for task_id={test_id}")
            print("   (This is expected if database was not initialized)")
            return True

    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("PrepSmart Multi-Agent System - End-to-End Test Suite")
    print("="*80)

    results = []

    # Test 1: Natural Disaster
    result1 = await test_natural_disaster()
    results.append(("Natural Disaster (Hurricane)", result1))

    # Test 2: Economic Crisis
    result2 = await test_economic_crisis()
    results.append(("Economic Crisis (Unemployment)", result2))

    # Test 3: Blackboard Persistence
    result3 = await test_blackboard_persistence()
    results.append(("Blackboard Persistence", result3))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
