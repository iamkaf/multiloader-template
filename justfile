set shell := ["bash", "-cu"]

default:
  @just --list

# Resolved at runtime so new version folders are picked up automatically.
version := shell("ls -1d */ | sed 's:/$::' | grep -E '^[0-9]' | sort -V | tail -n1")

list-versions:
  @ls -1d */ | sed 's:/$::' | grep -E '^[0-9]' | sort -V

versions: list-versions

latest:
  @echo {{version}}

# Check if a loader is included in a version's settings.gradle.
loader-enabled version loader:
  @if [ ! -f "{{version}}/settings.gradle" ]; then echo "false"; exit 0; fi
  @if (command -v rg >/dev/null 2>&1 && rg -q "^[[:space:]]*include\\([\"']{{loader}}[\"']\\)|^[[:space:]]*include[[:space:]]+[\"']{{loader}}[\"']" "{{version}}/settings.gradle") || \
     (! command -v rg >/dev/null 2>&1 && grep -Eq "^[[:space:]]*include\\([\"']{{loader}}[\"']\\)|^[[:space:]]*include[[:space:]]+[\"']{{loader}}[\"']" "{{version}}/settings.gradle"); then \
    echo "true"; \
  else \
    echo "false"; \
  fi

# Internal helper: run Gradle in a version folder, selecting Java based on `java_version=` in gradle.properties.
# Uses SDKMAN when available.
_gradle version *args:
  @cd "{{version}}" && \
  if command -v sdk >/dev/null 2>&1; then \
    if [ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]; then source "$HOME/.sdkman/bin/sdkman-init.sh"; fi; \
    java_version=$(sed -nE 's/^java_version=([0-9]+).*/\1/p' gradle.properties | head -n1); \
    if [ -n "$java_version" ]; then \
      case "$java_version" in \
        21) sdk use java 21.0.9-tem >/dev/null ;; \
        25) sdk use java 25.0.2-tem >/dev/null ;; \
        *) echo "Unsupported java_version=$java_version (expected 21 or 25)"; exit 1 ;; \
      esac; \
    fi; \
  fi; \
  ./gradlew {{args}}

# Run arbitrary Gradle tasks.
# - If the first arg is a version directory, run only there.
# - Otherwise run across all versions.
run first="" *rest:
  @if [ -z "{{first}}" ]; then echo "Usage: just run [version] <gradle args>"; exit 1; fi
  @if [ -d "{{first}}" ] && echo "{{first}}" | grep -Eq '^[0-9]'; then \
    if [ -z "{{rest}}" ]; then echo "Usage: just run [version] <gradle args>"; exit 1; fi; \
    just _gradle "{{first}}" {{rest}}; \
  else \
    for v in $(ls -1d */ | sed 's:/$::' | grep -E '^[0-9]' | sort -V); do \
      echo "==> $v"; just _gradle "$v" {{first}} {{rest}}; \
    done; \
  fi

build version="":
  @if [ -z "{{version}}" ]; then \
    for v in $(ls -1d */ | sed 's:/$::' | grep -E '^[0-9]' | sort -V); do \
      echo "==> $v"; \
      for loader in fabric forge neoforge; do \
        if [ "$(just loader-enabled "$v" "$loader")" = "true" ]; then \
          just _gradle "$v" :$loader:build; \
        else \
          echo "Skipping $v:$loader (not included in settings.gradle)"; \
        fi; \
      done; \
    done; \
  else \
    if [ ! -d "{{version}}" ]; then echo "Version {{version}} not found."; exit 1; fi; \
    for loader in fabric forge neoforge; do \
      if [ "$(just loader-enabled "{{version}}" "$loader")" = "true" ]; then \
        just _gradle "{{version}}" :$loader:build; \
      else \
        echo "Skipping {{version}}:$loader (not included in settings.gradle)"; \
      fi; \
    done; \
  fi

test version="":
  @if [ -z "{{version}}" ]; then \
    for v in $(ls -1d */ | sed 's:/$::' | grep -E '^[0-9]' | sort -V); do \
      echo "==> $v"; just _gradle "$v" test; \
    done; \
  else \
    if [ ! -d "{{version}}" ]; then echo "Version {{version}} not found."; exit 1; fi; \
    just _gradle "{{version}}" test; \
  fi

changed base="origin/main":
  @if ! git rev-parse --verify "{{base}}" >/dev/null 2>&1; then echo "Base ref {{base}} not found."; exit 1; fi
  @changed=$(git diff --name-only "{{base}}"...HEAD | grep -oP '^[0-9]+\\.[0-9]+[^/]*' | sort -u); \
  if [ -z "$changed" ]; then echo "No changed versions."; exit 0; fi; \
  echo "$changed"

build-changed base="origin/main":
  @if ! git rev-parse --verify "{{base}}" >/dev/null 2>&1; then echo "Base ref {{base}} not found."; exit 1; fi
  @changed=$(git diff --name-only "{{base}}"...HEAD | grep -oP '^[0-9]+\\.[0-9]+[^/]*' | sort -u); \
  if [ -z "$changed" ]; then echo "No changed versions."; exit 0; fi; \
  for v in $changed; do \
    echo "==> $v"; \
    for loader in fabric forge neoforge; do \
      if [ "$(just loader-enabled "$v" "$loader")" = "true" ]; then \
        just _gradle "$v" :$loader:build; \
      else \
        echo "Skipping $v:$loader (not included in settings.gradle)"; \
      fi; \
    done; \
  done

build-loader version loader *args:
  @if [ "$(just loader-enabled "{{version}}" "{{loader}}")" = "true" ]; then \
    just _gradle "{{version}}" :{{loader}}:build {{args}}; \
  else \
    echo "Skipping {{version}}:{{loader}} (not included in settings.gradle)"; \
  fi

test-changed base="origin/main":
  @if ! git rev-parse --verify "{{base}}" >/dev/null 2>&1; then echo "Base ref {{base}} not found."; exit 1; fi
  @changed=$(git diff --name-only "{{base}}"...HEAD | grep -oP '^[0-9]+\\.[0-9]+[^/]*' | sort -u); \
  if [ -z "$changed" ]; then echo "No changed versions."; exit 0; fi; \
  for v in $changed; do \
    echo "==> $v"; just _gradle "$v" test; \
  done

# Copy an existing version folder to create a new one.
new-version from to:
  @if [ -e "{{to}}" ]; then echo "Target {{to}} already exists."; exit 1; fi
  cp -r "{{from}}" "{{to}}"
