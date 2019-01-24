
# compile settings
cc = g++
defines = -DDEBUG_MODE #-DCOLOR_MODE #-DUSE_SYSLOG
linkings = -lpthread -lm -ldl -lrt -lopencv_core -lopencv_highgui -lopencv_imgproc
flags = $(defines) -O2 -g -std=c++17 -pedantic -Wall -Wextra

# source settings
src = $(wildcard ./*.cpp)
head = $(wildcard ./*.h)

dep = $(src:.cpp=.dep)
obj = $(src:.cpp=.o) 

#output settings
output = collector
all: $(output)
	@echo > /dev/null

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),test)
-include $(dep)
endif
endif

# static library
.PHONY: lib
lib: $(output).a
$(output).a: $(filter-out %main.o,$(obj))
	@echo "Creating static library $@.";\
	ar -cvq $@ $^ > /dev/null

.PHONY: test
test:
	@printf "";\
	$(MAKE) -C tests/ -s
	@printf "";\
	$(MAKE) run -C tests/ -s


# linking
$(output): $(obj)
	@echo "Linking project into collector.";\
	$(cc) $(flags) $^ -o $@ $(linkings)

# dependencies generating
%.dep: %.cpp
	@echo "Generating dependencies $@.";\
	$(cc) $(flags) -MM $< -MF $@ && \
	sed -i $@ -e 's_$*.o[ ]*:_$*.o $@: _' 2> /dev/null


# compiling
%.o : %.cpp
	@echo "Compiling $@.";\
	$(cc) $(flags) $(defines) -c $< -o $@ $(linkings)

# clean
.PHONY: clean
clean:
	@echo "Cleaning collector files.";\
	rm -rf *~ *.o *.gch *.dep $(output) $(output).a collector.a > /dev/null 2> /dev/null
	@printf "";\
	$(MAKE) clean -C tests/ -s
