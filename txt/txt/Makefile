
all: ibs.pdf

ibs.pdf:
		pdflatex bc.tex
		biber bc
		pdflatex bc.tex
		pdflatex bc.tex

.PHONY: clean
clean:
		@echo "";\
		rm bc.pdf bc.aux bc.bcf bc.log bc.run.xml bc.bbl bc.blg bc.toc 2> /dev/null > /dev/null