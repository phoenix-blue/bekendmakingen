.PHONY: test build package check clean

test:
	cd daemon && go test ./...

build:
	./scripts/build.sh

check: build
	./scripts/check-release.sh

package: build
	./scripts/package.sh

clean:
	rm -f toon2_bekendmakingen
	rm -rf dist
