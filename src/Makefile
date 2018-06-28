
.PHONY: all
all: collector
	@echo > /dev/null

collector:
	$(MAKE) -C core/ -s

.PHONY: lib
lib:
	@printf "";\
	$(MAKE) -C lib/ -s
	@printf "";\
	mv lib/libglobals.so . > /dev/null 2> /dev/null

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
	$(MAKE) clean -C lib/ -s
	@printf "";\
	$(MAKE) clean -C core/ -s
	@echo "Cleaning main directory.";\
	rm -rf libglobals.so collector > /dev/null 2> /dev/null
