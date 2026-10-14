"""
Tests for Ingestion Guard and Domain Alignment.
Covers: agency blocking, salary floor enforcement, location rules,
target/excluded title matching, job identifier extraction, and role scoring.
"""

import pytest
from ingest_guard import is_domain_aligned, extract_job_identifier, score_role

def test_agency_block():
    aligned, reason = is_domain_aligned("Director of Engineering", company="BairesDev")
    assert not aligned
    assert "Agency" in reason or "Staffing" in reason

    aligned, reason = is_domain_aligned("Engineering Manager", company="Robert Half")
    assert not aligned

    aligned, reason = is_domain_aligned("Director of Engineering", company="Acme Technologies")
    assert aligned

def test_salary_floor():
    # Min floor is configured to $180,000 in config.json
    aligned_low, reason_low = is_domain_aligned(
        title="Director of Engineering",
        company="TechCorp",
        salary="$120,000 - $140,000"
    )
    assert not aligned_low
    assert "below configured floor" in reason_low

    aligned_high, reason_high = is_domain_aligned(
        title="Director of Engineering",
        company="TechCorp",
        salary="$220,000 - $250,000"
    )
    assert aligned_high

    # Unstated salary should pass floor check
    aligned_unstated, _ = is_domain_aligned(
        title="Director of Engineering",
        company="TechCorp",
        salary=""
    )
    assert aligned_unstated

def test_location_rules():
    # Remote role allowed
    aligned_remote, _ = is_domain_aligned(
        title="Director of Engineering",
        company="TechCorp",
        location="Remote - US"
    )
    assert aligned_remote

    # Hybrid role in allowed metro (e.g. New York, Brooklyn, Manhattan)
    aligned_metro, _ = is_domain_aligned(
        title="Director of Engineering",
        company="TechCorp",
        location="Hybrid - New York, NY"
    )
    assert aligned_metro

    # Hybrid/Onsite role outside target metro
    aligned_outside, reason_outside = is_domain_aligned(
        title="Director of Engineering",
        company="TechCorp",
        location="Onsite - Seattle, WA"
    )
    assert not aligned_outside
    assert "outside target metro" in reason_outside

def test_title_match_and_exclusions():
    # Direct target match
    aligned_target, _ = is_domain_aligned("Director of Engineering", company="TechCorp")
    assert aligned_target

    # Excluded title match
    aligned_excluded, reason_ex = is_domain_aligned("Junior Software Developer", company="TechCorp")
    assert not aligned_excluded
    assert "Excluded Title Match" in reason_ex

    aligned_intern, reason_in = is_domain_aligned("Software Engineering Intern", company="TechCorp")
    assert not aligned_intern
    assert "Excluded Title Match" in reason_in

    # Senior leadership fallback
    aligned_vp, _ = is_domain_aligned("VP of Technology", company="TechCorp")
    assert aligned_vp

    # Role neither matching target nor leadership level
    aligned_other, reason_other = is_domain_aligned("Account Executive", company="TechCorp")
    assert not aligned_other

def test_extract_job_identifier():
    li_url = "https://www.linkedin.com/jobs/view/3928172635?trackingId=abc&refId=123"
    assert extract_job_identifier(li_url) == "li_3928172635"

    builtin_url = "https://builtin.com/job/engineering/director-of-platform/2048593?search=1"
    assert extract_job_identifier(builtin_url) == "builtin_2048593"

    generic_url = "https://boards.greenhouse.io/examplecorp/jobs/5544332"
    assert extract_job_identifier(generic_url) == "https://boards.greenhouse.io/examplecorp/jobs/5544332"

def test_score_role_differentiates_sensibly():
    high_role = score_role("Director of Engineering", "TechCorp", "$240,000", "today")
    med_role = score_role("Director of Engineering", "BudgetCorp", "$180,000", "today")
    low_role = score_role("Junior Operations Assistant", "SmallCo", "$60,000", "30 days ago")

    assert 0 <= high_role <= 100
    assert 0 <= med_role <= 100
    assert 0 <= low_role <= 100

    assert high_role > med_role
    assert med_role > low_role
