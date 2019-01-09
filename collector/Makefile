
# compile settings
cc = g++
defines = -DDEBUG_MODE #-DCOLOR_MODE #-DUSE_SYSLOG
linkings = -lpthread -lm -ldl -lrt
flags = $(defines) -O2 -g -std=c++17 -pedantic -Wall -Wextra

# source settings
src = $(wildcard *.cpp)
head = $(wildcard *.h)

dep = $(src:.cpp=.dep)
obj = $(src:.cpp=.o) 

#output settings
output = collector
all: $(output)
	@echo > /dev/null

ifneq ($(MAKECMDGOALS),clean)
-include $(dep)
endif

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
	$(cc) $(flags) $(defines) -c $< -o $@

# clean
.PHONY: clean
clean:
	@echo "Cleaning.";\
	rm -rf *~ *.o *.gch *.dep $(output) > /dev/null 2> /dev/null
