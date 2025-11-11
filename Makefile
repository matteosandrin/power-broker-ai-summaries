summary:
	python main.py summary

convert:
	python main.py convert

clean:
	rm -rf ./output

.PHONY: run clean