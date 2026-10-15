# Orcamatic static site for GitHub Pages

This directory is the complete, deployable public website for `orcamatic.com`.
It is deliberately independent of the existing application and requires **no server, database, Node.js install, or build command**. GitHub Pages publishes these files exactly as they are.

## What is included

- Product landing page for ORCA
- Product, About, Pricing, Journal, and legal pages
- Static copies of the product journal posts
- SEO basics: canonical URLs, `robots.txt`, `sitemap.xml`, and web manifest
- Responsive navigation, mobile menu, native FAQ, and reduced-motion support
- `CNAME` with the production custom domain: `orcamatic.com`

The public site is static-only. No server-backed or data-driven feature is deployed from this folder.

## Important files

| Path | Purpose |
| --- | --- |
| `index.html` | Homepage |
| `assets/site.css` | Shared responsive styling |
| `assets/site.js` | Small, dependency-free navigation and reveal behavior |
| `CNAME` | Records the production domain `orcamatic.com` — also set it in Settings → Pages |
| `sitemap.xml` / `robots.txt` | Search-engine discovery |
| `404.html` | Friendly GitHub Pages not-found page |

All public URLs assume the custom domain is the site root, for example
`https://orcamatic.com/pricing/`.

## Automated deployment

The workflow at [`.github/workflows/deploy-github-pages.yml`](../.github/workflows/deploy-github-pages.yml)
validates local links, anchors, assets, the manifest, and the sitemap, then
publishes this directory whenever a site or deployment change is merged into
`main`. Pull requests run the checks without deploying. A manual run only deploys
when `main` is selected; unmerged feature branches are never published.

Only this directory is uploaded. The repository's ZIP archive, scripts, and
other repository files are not part of the deployment.

### One-time GitHub setup

After this change reaches `main`:

1. Open **GitHub repository → Settings → Pages**.
2. Under **Build and deployment**, choose **GitHub Actions** as the source.
3. In **Settings → Pages**, enter `orcamatic.com` as the **Custom domain** and
   save it. With GitHub Actions, the `CNAME` file alone does not configure the
   domain. These pages use root-relative URLs and require the custom domain;
   the default `/orcamatic-pages/` project URL is not their intended base path.
4. Open the **Actions** tab and run **Deploy Orcamatic site to GitHub Pages** on
   `main`, or rerun the initial deployment if it failed before Pages was enabled.
5. Wait for the deployment job to complete. GitHub will show the Pages URL in
   the deployment details. Configure the DNS records below, then enable
   **Enforce HTTPS** once the DNS and certificate checks succeed.

> The workflow itself needs no secret values. GitHub's deployment token is supplied
> by the Actions runtime.

## Pointing `orcamatic.com` to GitHub Pages

The domain can remain registered at Spaceship. Only the website DNS records need
changing. Do not change email-related records (MX, DKIM, SPF) if you use email on
this domain.

In the DNS provider that currently controls the domain, remove or replace the old
website records for the root (`@`) and add these GitHub Pages records:

| Type | Host / Name | Value |
| --- | --- | --- |
| `A` | `@` | `185.199.108.153` |
| `A` | `@` | `185.199.109.153` |
| `A` | `@` | `185.199.110.153` |
| `A` | `@` | `185.199.111.153` |
| `AAAA` | `@` | `2606:50c0:8000::153` |
| `AAAA` | `@` | `2606:50c0:8001::153` |
| `AAAA` | `@` | `2606:50c0:8002::153` |
| `AAAA` | `@` | `2606:50c0:8003::153` |

Optional, but recommended for visitors using `www`:

| Type | Host / Name | Value |
| --- | --- | --- |
| `CNAME` | `www` | `mabk26.github.io` |

Notes:

- If Spaceship says the record conflicts, remove the previous root `A` / `AAAA`
  records that pointed at the old web host. Keep unrelated mail records.
- Do not put `http://` or `https://` in any DNS value.
- If a third party such as Cloudflare controls your DNS, make the changes there,
  not in Spaceship. During GitHub verification, set a Cloudflare record to
  **DNS only** rather than proxied.
- GitHub may offer a domain-verification TXT record under **Settings → Pages**.
  Add the exact host and value GitHub displays before enforcing HTTPS. This protects
  the domain from being claimed by another GitHub Pages site.
- DNS and certificate issuance can take from a few minutes to 24 hours. Do not
  cancel the old host until `https://orcamatic.com` has loaded successfully from
  a normal browser and the GitHub Pages HTTPS check is green.

## Updating the website later

1. Edit the files inside `git_page_wa/` only.
2. Test locally if needed:

   ```bash
   # From the repository root:
   python3 scripts/validate_site.py
   python3 -m http.server 4173 --bind 0.0.0.0 --directory git_page_wa
   ```

   Then open `http://localhost:4173`.
3. Merge the change to `main`. The GitHub Pages workflow deploys it automatically.

There are no generated files to rebuild. If you add a new public page, update
`sitemap.xml` and add the route to the footer or navigation where appropriate.
