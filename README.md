# ATLAS Research Intelligence — refined interface and stability update

## Deploy to Streamlit Community Cloud
Upload the files in this directory to the root of your existing GitHub repository (including `i18n.py`, `science.py`, `book.py`, `medical.py`, and `.streamlit/config.toml`). Keep `app.py` as the entry point. Set `OPENAI_API_KEY` only in Streamlit Cloud **Secrets**. Do not commit secrets.

## Interface
Choose Arabic, German, or English using the selector at the top of the sidebar. The interface translations are independent from the language chosen for analysis, report, or book output. The visible ATLAS logo is a larger, multicolor microscope; the version string and extra promotional subtitle are removed.

## Scientific limits
- Descriptive table statistics are calculated from extracted values and require checking against the original PDF.
- Image pixel statistics are not chart digitization.
- The medical image mask is a **threshold demonstration**, not a validated anatomical segmentation or diagnosis.
- The linear what-if model is **not** a physical simulation fitted to the uploaded thesis.
- Book and manuscript PDFs are drafts requiring editorial, scientific, copyright, and publication review.
- AI requests incur OpenAI API usage charges. No patient identifiers should be uploaded without a compliant deployment and proper authorization.

## Checks
Run `python -m compileall -q .` and `python tests/test_regressions.py`. The tests check translations, tab rendering code, table duplicate headers, numeric parsing, and source import syntax. End-to-end Streamlit Cloud, AI API, and real scientific/clinical validation must be tested separately.
