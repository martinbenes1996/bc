
.PHONY: all
all: bc_client
	@echo > /dev/null

bc_client:
	$(MAKE) -C client/ -s
	cp client/bc_client .

.PHONY: doxygen
doxygen:
	@echo "Generating documentation";\
	doxygen Doxyfile 2> /dev/null > /dev/null

.PHONY: run
run:
	@printf "";\
	true

.PHONY: clean
clean:
	@printf "";\
	$(MAKE) clean -C client/ -s
	@echo "Cleaning main directory.";\
	rm -rf bc_client > /dev/null 2> /dev/null
