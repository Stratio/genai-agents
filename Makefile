change-version:
	bin/change-version.sh $(version)

compile:
	bin/compile.sh

test:
	bin/test.sh

package:
	bin/package.sh

deploy:
	bin/deploy.sh

clean:
	bin/clean.sh
