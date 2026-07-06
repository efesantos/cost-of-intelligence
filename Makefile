# Reproduce every number with `make all` (G5). Requires ../tokenlab installed.
PY=python
export HF_HUB_DISABLE_PROGRESS_BARS=1

.PHONY: all corpus fertility prices wages instruments figures test clean
all: corpus fertility prices wages instruments figures

corpus:      ; $(PY) src/corpus.py
fertility:   ; $(PY) src/run_fertility.py
prices:      ; $(PY) src/prices.py
wages:       ; $(PY) src/wages.py
instruments: ; $(PY) src/instruments.py
figures:     ; $(PY) src/figures.py
refresh-prices: ; $(PY) src/prices.py   # final-week live price refresh
test:        ; pytest -q
clean:       ; rm -rf data/*.parquet figures/*.png figures/*.svg
