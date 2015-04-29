TEX = pdflatex

default: paper

paper:	
	$(TEX)  report.tex 
	bibtex -min-crossrefs=100 report
	$(TEX)   report.tex 
	$(TEX)   report.tex 
	$(TEX)   report.tex 

clean:
	rm -f 	*.aux *.bbl *.blg *.dvi *.log *.ps *.pdf

tidy:
	rm -f 	*.aux *.bbl *.blg *.dvi *.log 

view:   report.pdf
	xpdf report.pdf&
