all:
	@echo "Please run 'make clean' to remove redacted PDF files."

clean:
	@rm -fv *_redacted.pdf
