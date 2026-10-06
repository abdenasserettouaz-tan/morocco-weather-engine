from pathlib import Path


def test_mobile_runtime_controls_exist():
    html = Path('app/mobile/index.html').read_text(encoding='utf-8')
    assert 'id="refreshBtn"' in html
    assert 'id="netDot"' in html
    assert 'id="dataStatus"' in html
