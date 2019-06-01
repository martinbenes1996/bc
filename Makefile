
.PHONY: zip
zip:
	@echo "Copy project data.";\
	mkdir xbenes49 
	
	@echo "\tData";\
	mkdir xbenes49/data
	@printf "";\
	cp -r data/c*/ xbenes49/data/
	@printf "";\
	cp -r data/d*/ xbenes49/data/
	@printf "";\
	cp -r data/e*/ xbenes49/data/
	@printf "";\
	cp -r data/o*/ xbenes49/data/
	@printf "";\
	cp data/show.py xbenes49/data/
	
	@echo "\tMonitor.";\
	mkdir xbenes49/monitor
	@printf "";\
	cp monitor/*.py xbenes49/monitor/
	@printf "";\
	cp monitor/*.sh xbenes49/monitor/
	@printf "";\
	cp monitor/README.md xbenes49/monitor/
	@printf "";\
	mkdir xbenes49/monitor/classifiers
	@printf "";\
	cp monitor/classifiers/*.sav xbenes49/monitor/classifiers/
	@printf "";\
	cp monitor/classifiers/*set.json xbenes49/monitor/classifiers/
	@printf "";\
	cp monitor/classifiers/*.py xbenes49/monitor/classifiers/
	@printf "";\
	cp -r monitor/optimizers xbenes49/monitor/
	@printf "";\
	cp -r monitor/tests xbenes49/monitor

	@echo "\tModule.";\
	mkdir xbenes49/module
	@printf "";\
	cp -r module/mcu.c xbenes49/module/
	@printf "";\
	cp -r module/mcu_serial.c xbenes49/module/
	@printf "";\
	cp module/*.json xbenes49/module/
	@printf "";\
	cp module/*.png xbenes49/module/
	@printf "";\
	cp module/board.zip xbenes49/module/

	@echo "\tText";\
	cp text/xbenes49.pdf xbenes49/ > /dev/null 2> /dev/null
	@printf "";\
	cp README_output.md xbenes49/README.md > /dev/null 2> /dev/null
	@printf "";\
	cp -r sources/pirstd.pdf xbenes49/pirstd.pdf

	@echo "Copy environment.";\
	cp -r monitor/env xbenes49/monitor/

	@echo "Zipping.";\
	tar -czvf xbenes49.tar.gz xbenes49/* > /dev/null 2> /dev/null
	@printf "";\
	rm -rf xbenes49
	
.PHONY: clean
clean:
	@echo "Cleaning main directory.";\
	rm -rf xbenes49 xbenes49.tar.gz 2> /dev/null
