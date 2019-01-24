
# compile settings
cc = g++
defines = -DDEBUG_MODE #-DCOLOR_MODE #-DUSE_SYSLOG
linkings = -lpthread -lm -ldl -lrt -lopencv_core -lopencv_highgui -lopencv_imgproc
flags = $(defines) -O2 -g -std=c++17 -pedantic -Wall -Wextra -L. -I.. -I.

# source settings
src = $(wildcard *.cpp)
head = $(wildcard *.h)

dep = $(src:.cpp=.dep)
obj = $(src:.cpp=.o) 

#output settings
output = test
all: collector.a $(output)
	@echo > /dev/null

collector.a:
	@printf "";\
	$(MAKE) lib -C .. -s
	@printf "";\
	cp ../collector.a .

.PHONY: run
run: $(OUTPUT)
	@printf "";\
	./$^

ifneq ($(MAKECMDGOALS),clean)
-include $(dep)
endif

# linking
$(output): $(obj)
	@echo "Linking test.";\
	$(cc) $(flags) -static collector.a $^ -o $@ $(linkings)

# dependencies generating
%.dep: %.cpp
	@echo "Generating dependencies $@.";\
	$(cc) $(flags) -MM $< -MF $@ && \
	sed -i $@ -e 's_$*.o[ ]*:_$*.o $@: _' 2> /dev/null


# compiling
%.o : %.cpp
	@echo "Compiling $@.";\
	$(cc) $(flags) $(defines) -c $^ -o $@ $(linkings)

# clean
.PHONY: clean
clean:
	@echo "Cleaning test files.";\
	rm -rf *~ *.o *.gch *.dep $(output) collector.a > /dev/null 2> /dev/null
