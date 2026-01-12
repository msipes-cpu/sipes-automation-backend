# Directive: SEO & Content Domain Policy

> [!CRITICAL]
> **SEO Content MUST Live on the Main Domain**
> All SEO-driven content (Blogs, Articles, Landing Pages intended for inorganic traffic) MUST be published and indexed ONLY on `sipesautomation.com`. 

## 1. Domain Enforcement Rules
*   **Main Domain (`sipesautomation.com`)**: Hosting for all marketing, branding, and `/blog` content.
*   **Client Subdomains (`client.sipesautomation.com`)**: Strictly for **Application Utility** (Dashboards, Client Portals, Tools).
*   **NEVER** serve blog posts or marketing pages on a client subdomain. It dilutes SEO authority (duplicate content issues) and confuses the user journey.

## 2. Technical Implementation Requirements
*   **Middleware Redirects:** The application logic MUST detect if a user attempts to access `/blog/*` from a subdomain and **301 Redirect** them to `https://sipesautomation.com/blog/*`.
*   **Canonical Tags:** All blog pages must have a self-referencing canonical tag pointing to `https://sipesautomation.com/...`.

## 3. Deployment Checklist
Before publishing any new article:
1.  [ ] Verify the URL is `sipesautomation.com/blog/slug`.
2.  [ ] Check that accessing `subdomain.sipesautomation.com/blog/slug` redirects to the main domain.
3.  [ ] Ensure internal links (Navbar/Footer) on subdomains point to the absolute URL (`https://sipesautomation.com/blog`) rather than a relative path (`/blog`).

## 4. Why This Matters
*   **Domain Authority:** Concentrating all content on one domain builds higher authority / rank faster.
*   **Brand Trust:** Clients seeing "malak.sipesautomation.com" for a general article looks like a software bug or a leaked instance.
