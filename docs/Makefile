
SRCS=$(wildcard *.json)
PNGS=$(SRCS:.json=.png)

.PHONY: all
all: $(PNGS)

%.png : %.json
	wavedrompy -i $< | inkscape --file - --export-dpi 300 --export-png $@

.PHONY: clean
clean:
	rm -rf $(PNGS)
