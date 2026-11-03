# Makefile -- build with latexmk.
# Targets: all (anonymous submission), camera (proceedings), full (ePrint), check, anon, clean.
MAIN ?= main
LIMIT ?= 30
# Skill scripts: a project set up with install.sh has them in ../.claude/skills; otherwise point
# CRA_HOME at the toolkit checkout (make check CRA_HOME=~/zk-research-agents).
CRA_HOME ?= ../../..
SKILLS ?= $(firstword $(wildcard ../.claude/skills) $(if $(CRA_HOME),$(CRA_HOME)/skills))
# The project bibliography (owned by lit-scout, checked by bib-verify) lives one level up.
BIB ?= ../refs.bib

all: llncs.cls
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

camera: llncs.cls
	latexmk -pdf -interaction=nonstopmode -halt-on-error main_camera.tex

full: llncs.cls
	latexmk -pdf -interaction=nonstopmode -halt-on-error main_full.tex

llncs.cls:
	@kpsewhich llncs.cls >/dev/null 2>&1 || sh ./fetch_llncs.sh

check: skills all
	python3 $(SKILLS)/camera-ready/scripts/pdf_checks.py $(MAIN).pdf --log $(MAIN).log --limit $(LIMIT)

anon: skills all
	python3 $(SKILLS)/anonymize-check/scripts/anon_check.py sections $(BIB) macros.tex $(MAIN).pdf \
	  $(if $(wildcard .denylist.txt),--deny-file .denylist.txt,)

skills:
	@test -n "$(SKILLS)" -a -d "$(SKILLS)" || { echo "skill scripts not found: run install.sh on the project or pass CRA_HOME=<toolkit>"; exit 1; }

clean:
	latexmk -C $(MAIN).tex; latexmk -C main_camera.tex; latexmk -C main_full.tex
	rm -f *.bbl *.run.xml

.PHONY: all camera full check anon skills clean
