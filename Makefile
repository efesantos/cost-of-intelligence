# Reproduce every number with `make all` (G5). Requires ../tokenlab installed.
# `make results` regenerates every derived number, figure and report from the
# committed data, offline. `make paper` builds paper/main.tex and paper/main.pdf.
PY=python
export HF_HUB_DISABLE_PROGRESS_BARS=1

.PHONY: all corpus fertility udhr prices wages ilostat aei instruments figures adoption sensitivity web results paper test clean
all: corpus fertility udhr prices wages ilostat aei results

corpus:      ; $(PY) src/corpus.py
fertility:   ; $(PY) src/run_fertility.py
udhr:        ; $(PY) src/udhr.py
prices:      ; $(PY) src/prices.py
wages:       ; $(PY) src/wages.py
ilostat:     ; $(PY) src/ilostat.py
aei:         ; $(PY) src/aei.py
instruments: ; $(PY) src/instruments.py
figures:     ; $(PY) src/figures.py && $(PY) src/figures_instruments.py
adoption:    ; $(PY) src/adoption.py
sensitivity: ; $(PY) src/sensitivity.py
web:         ; $(PY) src/export_web.py
results: instruments figures adoption sensitivity web
refresh-prices: ; $(PY) src/prices.py   # final-week live price refresh; then `make results`
paper:       ; $(PY) paper/build.py
test:        ; pytest -q
clean:       ; rm -rf data/*.parquet figures/*.png figures/*.svg figures/*.pdf
