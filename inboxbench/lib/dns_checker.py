
import dns.resolver
import logging

def check_dns_vitals(email, selector="default"):
    """
    Checks SPF, DKIM (if selector provided), and DMARC for a given email domain.
    
    Args:
        email (str): The email address to check.
        selector (str): The DKIM selector (default: 'default', 'google', etc. logic handling later).
    
    Returns:
        dict: { "spf": bool, "dkim": bool, "dmarc": bool }
    """
    domain = email.split("@")[1]
    results = {"spf": False, "dkim": False, "dmarc": False}
    
    # 1. SPF Check
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            txt_record = str(rdata).strip('"')
            if txt_record.startswith("v=spf1"):
                results["spf"] = True
                break
    except Exception as e:
        logging.warning(f"SPF check failed for {domain}: {e}")
        
    # 2. DMARC Check
    try:
        dmarc_domain = f"_dmarc.{domain}"
        answers = dns.resolver.resolve(dmarc_domain, 'TXT')
        for rdata in answers:
            txt_record = str(rdata).strip('"')
            if txt_record.startswith("v=DMARC1"):
                results["dmarc"] = True
                break
    except Exception as e:
        # NXDOMAIN or other error means no DMARC
        logging.warning(f"DMARC check failed for {domain}: {e}")

    # 3. DKIM Check
    # Without knowing the exact selector, we can't be 100% sure.
    # Common selectors: 'default', 'google', 'k1', 's1'.
    # We will try a few common ones if selector is default, or trust the input.
    selectors_to_try = [selector] if selector != "default" else ["default", "google", "k1", "20230601"] 
    
    for sel in selectors_to_try:
        try:
            dkim_domain = f"{sel}._domainkey.{domain}"
            answers = dns.resolver.resolve(dkim_domain, 'TXT')
            for rdata in answers:
                txt_record = str(rdata).strip('"')
                if txt_record.startswith("v=DKIM1") or "p=" in txt_record:
                    results["dkim"] = True
                    break
        except:
            continue
        
        if results["dkim"]:
            break
            
    return results
