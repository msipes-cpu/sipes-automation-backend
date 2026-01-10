
import urllib.parse
from typing import Dict, Any, List

def parse_apollo_url(url: str) -> Dict[str, Any]:
    """
    Parses an Apollo People Search URL and extracts filter parameters.
    Returns a dictionary suitable for passing to apollo_search or directly to the API.
    """
    parsed = urllib.parse.urlparse(url)
    # Apollo URLs often have the query params in the fragment after '?' if using hash routing
    # e.g. https://app.apollo.io/#/people?page=1...
    # So we check parsed.query first, if empty check parsed.fragment
    
    query_string = parsed.query
    if not query_string and '?' in parsed.fragment:
        query_string = parsed.fragment.split('?', 1)[1]
    
    if not query_string:
        return {}
        
    params = urllib.parse.parse_qs(query_string)
    
    payload = {
        "page": 1,
        "per_page": 100 # Default to max for efficiency
    }
    
    # Mapping
    # Helper to extracting lists
    def get_list(param_name):
        # parse_qs returns a list of values.
        # Sometimes Apollo uses [] in keys, e.g., personTitles[]
        val = params.get(param_name) or params.get(f"{param_name}[]")
        return val if val else []

    # Job Titles
    titles = get_list("personTitles")
    if titles:
        payload["person_titles"] = titles
        
    # Locations
    locations = get_list("personLocations")
    if locations:
        payload["person_locations"] = locations
        
    # Employee Ranges
    employees = get_list("organizationNumEmployeesRanges")
    if employees:
        payload["organization_num_employees_ranges"] = employees
        
    # Industry Tags
    industry_ids = get_list("organizationIndustryTagIds")
    if industry_ids:
        payload["organization_industry_tag_ids"] = industry_ids
        
    # Keywords
    keywords = get_list("qOrganizationKeywordTags")
    if keywords:
        payload["q_organization_keyword_tags"] = keywords
        
    # Email Status (Verified)
    email_status = get_list("contactEmailStatusV2")
    if email_status:
        payload["contact_email_status"] = email_status
        
    # Excluded keywords?
    # qNotOrganizationKeywordTags[]
    excluded_keywords = get_list("qNotOrganizationKeywordTags")
    if excluded_keywords:
        payload["q_not_organization_keyword_tags"] = excluded_keywords

    # Revenue Range
    # revenueRange[min], revenueRange[max]
    revenue_min = params.get("revenueRange[min]") or params.get("revenueRange[min][]")
    revenue_max = params.get("revenueRange[max]") or params.get("revenueRange[max][]")
    
    if revenue_min or revenue_max:
        payload["revenue_range"] = {}
        if revenue_min:
            try:
                payload["revenue_range"]["min"] = int(revenue_min[0])
            except: pass
        if revenue_max:
            try:
                payload["revenue_range"]["max"] = int(revenue_max[0])
            except: pass

    # Sort
    # sortAscending, sortByField
    
    return payload

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        print(json.dumps(parse_apollo_url(sys.argv[1]), indent=2))
    else:
        # Test
        test_url = "https://app.apollo.io/#/people?personTitles[]=ceo&personLocations[]=United%20States"
        print(f"Test URL: {test_url}")
        print(json.dumps(parse_apollo_url(test_url), indent=2))
