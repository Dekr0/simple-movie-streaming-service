target=		prjcode
allFiles=       Makefile prjcode
scpDir=		chengxua@ug05.cs.ualberta.ca:~/291
# ------------------------------------------------------------


starter: 
	cp a2.db test.db
	python3 main.py test.db

local:
	cp a2.db test.db
	python main.py test.db

tar:
	touch $(target).tgz
	mv $(target).tgz  x$(target).tgz
	tar -cvzf $(target).tgz $(allFiles)
	gzip $(target).tgz

scp:
	scp $(target).tgz $(scpDir)

clean:
	rm -f test.db

