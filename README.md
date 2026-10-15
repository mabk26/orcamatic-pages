# Orcamatic website

The public website for **[orcamatic.com](https://orcamatic.com)**, extracted from
`git_page_wa.zip`. It is a plain HTML, CSS, and JavaScript site: no install, build
step, backend, or API keys are needed.

## Repository layout

- [`git_page_wa/`](git_page_wa/) — the deployable website, including the homepage,
  product/pricing pages, journal, legal pages, assets, and custom 404 page.
- [`.github/workflows/deploy-github-pages.yml`](.github/workflows/deploy-github-pages.yml)
  — validates the site and publishes **only `git_page_wa/`** to GitHub Pages.
- [`scripts/validate_site.py`](scripts/validate_site.py) — dependency-free checks
  for internal links, anchors, assets, manifest, and sitemap.
- `git_page_wa.zip` — the original upload, retained for reference. Edit the
  extracted files, not the archive.

## Publish with GitHub Pages

1. Merge the website and deployment workflow into `main`.
2. Open [Settings → Pages](https://github.com/mabk26/orcamatic-pages/settings/pages).
3. Under **Build and deployment → Source**, select **GitHub Actions**.
   Do **not** select “Deploy from a branch”: the website is in `git_page_wa/`,
   and the workflow publishes that folder as the website root.
4. In **Custom domain**, enter **`orcamatic.com`** and save it. The Actions
   deployment does not configure the domain merely from the `CNAME` file.
5. Follow the [DNS instructions](git_page_wa/README.md#pointing-orcamaticcom-to-github-pages)
   to point the domain to GitHub Pages. Keep email-related DNS records unchanged.
6. Open [Actions](https://github.com/mabk26/orcamatic-pages/actions/workflows/deploy-github-pages.yml).
   If the initial run failed before Pages was enabled, rerun it, or select
   **Run workflow → main** after enabling Pages.
7. Once GitHub's DNS and certificate checks succeed, enable **Enforce HTTPS**
   in Settings → Pages.

Future website changes merged into `main` deploy automatically. Pull requests
only validate the site; they never publish it. A manually triggered workflow also
only publishes when run on `main`.

**Custom domain required:** the supplied pages use root-relative URLs such as
`/assets/site.css` and canonical URLs on `https://orcamatic.com`. They are intended
for that domain, not the `/orcamatic-pages/` project-site subpath. Configure the
custom domain before relying on the live site.

## Preview and validate locally

From the repository root:

```bash
python3 scripts/validate_site.py
python3 -m http.server 4173 --bind 0.0.0.0 --directory git_page_wa
```

Open port **4173** in your development environment, or `http://localhost:4173`
when running on your own computer. Stop the server with Ctrl+C.

See the [website deployment guide](git_page_wa/README.md) for DNS records and
content-maintenance details.
