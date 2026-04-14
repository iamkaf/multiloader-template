set shell := ["bash", "-euo", "pipefail", "-c"]

default:
  @just --list

list-versions:
  @find versions -mindepth 2 -maxdepth 2 -type f -name 'gradle.properties' -printf '%h\n' | xargs -r -n1 basename | sort -V

list-loaders version:
  @grep '^project.enabled-loaders=' "versions/{{version}}/gradle.properties" | head -n1 | cut -d= -f2- | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | sed '/^$/d'

list-nodes:
  @for props in versions/*/gradle.properties; do version=$(basename "$(dirname "$props")"); loaders=$(sed -nE 's/^project\.enabled-loaders=(.*)$/\1/p' "$props" | head -n1); for loader in $(printf '%s\n' "$loaders" | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | sed '/^$/d'); do echo "$version-$loader"; done; done | sort -V

projects:
  @./gradlew projects --console=plain

clean-generated:
  @rm -rf .stonecutter common/versions fabric/versions forge/versions neoforge/versions

build node:
  @if ! just list-nodes | grep -Fxq "{{node}}"; then \
    echo "Unknown Stonecutter node: {{node}}"; \
    exit 1; \
  fi
  @version="{{node}}"; loader="${version##*-}"; version="${version%-*}"; \
  ./gradlew ":$loader:$version:build" --console=plain

run-client node:
  @if ! just list-nodes | grep -Fxq "{{node}}"; then \
    echo "Unknown Stonecutter node: {{node}}"; \
    exit 1; \
  fi
  @version="{{node}}"; loader="${version##*-}"; version="${version%-*}"; \
  ./gradlew ":$loader:$version:runClient" --console=plain

build-all:
  @for node in $(just list-nodes); do \
    echo "==> $node"; \
    just build "$node"; \
  done

boot-check node timeout="80":
  @if ! just list-nodes | grep -Fxq "{{node}}"; then \
    echo "Unknown Stonecutter node: {{node}}"; \
    exit 1; \
  fi
  @node="{{node}}"; \
  version="${node%-*}"; \
  loader="${node##*-}"; \
  log="/tmp/$node.run.log"; \
  set +e; \
  timeout "{{timeout}}"s ./gradlew ":$loader:$version:runClient" --console=plain > "$log" 2>&1; \
  status=$?; \
  set -e; \
  if [ "$status" -ne 0 ] && [ "$status" -ne 124 ]; then \
    tail -n 160 "$log"; \
    exit "$status"; \
  fi; \
  grep -q 'Initializing Template on' "$log"; \
  grep -q 'Backend library:' "$log"; \
  echo "Boot OK: $node (status=$status)"

boot-check-all timeout="80":
  @for node in $(just list-nodes); do \
    echo "==> $node"; \
    just boot-check "$node" "{{timeout}}"; \
  done
