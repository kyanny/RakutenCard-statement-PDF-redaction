all:
	@echo "Please run 'make clean' to remove redacted PDF files."

clean:
	@rm -fv *_{redacted,highlighted}.pdf

clobber:
	@rm -fv *.pdf
