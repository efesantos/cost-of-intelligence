"""Identity + arithmetic tests for the instruments (Task B-5 acceptance).

These do not require network: they read the committed parquet artifacts. If the
pipeline has not been run in this checkout, they skip.
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import instruments as I  # noqa: E402


def test_p_blend_endpoints():
    # r=0 -> input only; large r -> output only; r=3 default weighting
    assert I.p_blend(2.0, 10.0, r=0.0) == pytest.approx(2.0)
    assert I.p_blend(2.0, 10.0, r=1e9) == pytest.approx(10.0, rel=1e-6)
    assert I.p_blend(2.0, 10.0, r=3.0) == pytest.approx((2 + 30) / 4)


@pytest.mark.skipif(not (ROOT / "data" / "instruments.parquet").exists(),
                    reason="pipeline artifacts not present")
def test_english_surcharge_zero_and_linearity():
    df = I.compute(write=False)
    en = df[df.language == "eng_Latn"]
    assert (en["surcharge"].abs() < 1e-9).all()
    # doubling the bundle exactly doubles work_minutes
    d2 = I.compute(bundle_etok=2_000_000.0, write=False)
    m = df.merge(d2, on=["language", "family"], suffixes=("", "_2x")).dropna(subset=["work_minutes_ppp"])
    ratio = (m["work_minutes_ppp_2x"] / m["work_minutes_ppp"]).round(9)
    assert (ratio == 2.0).all()


@pytest.mark.skipif(not (ROOT / "data" / "instruments.parquet").exists(),
                    reason="pipeline artifacts not present")
def test_compute_does_not_write_by_default(tmp_path, monkeypatch):
    before = (ROOT / "data" / "instruments.parquet").stat().st_mtime
    I.compute(r=9, write=False)      # must NOT overwrite canonical file
    after = (ROOT / "data" / "instruments.parquet").stat().st_mtime
    assert before == after
