from pathlib import Path
import ast
app = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
ast.parse(app)
assert "page_title='ATLAS EAST | Research Intelligence'" in app
assert '>ATLAS EAST</div>' in app
assert "key='atlas_page', horizontal=True" in app
assert "tab_names=[T(k)" in app and 'tabs=st.tabs(tab_names)' in app
assert "if selected_page == 'home':" in app
assert "st.stop()" in app
assert "MICROSCOPE_SVG" in app
print('PASS: ATLAS EAST branding, horizontal navigation, unchanged research tabs')
