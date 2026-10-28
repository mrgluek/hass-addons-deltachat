#!/usr/bin/env bash
# Image helpers for one add-on, driven by addons/<addon>/config.yaml.
#
#   addon-image.sh meta <addon>       print image=, version=, platforms= (for $GITHUB_OUTPUT)
#   addon-image.sh published <addon>  exit 0 only if <image>:<version> exists in the registry
#                                     for every arch listed under `arch:`
#
# Home Assistant pulls <image>:<version> for the user's arch, so "published" is the
# condition for a version bump to be safe to show to users.
set -euo pipefail

cmd="${1:?usage: $0 meta|published <addon>}"
addon="${2:?usage: $0 meta|published <addon>}"
cfg="addons/${addon}/config.yaml"

# Top-level scalar from config.yaml, quotes stripped
field() { grep "^$1:" "$cfg" | head -n1 | awk '{print $2}' | tr -d "\"'"; }

# Items of the top-level `arch:` list
arches() { awk '/^arch:/{f=1; next} f && /^ *- /{print $2; next} f{exit}' "$cfg" | tr -d "\"'"; }

# HA arch name -> docker platform
platform() {
  case "$1" in
    aarch64) echo "linux/arm64" ;;
    amd64) echo "linux/amd64" ;;
    armv7) echo "linux/arm/v7" ;;
    armhf) echo "linux/arm/v6" ;;
    i386) echo "linux/386" ;;
    *) echo "Unknown arch '$1' in $cfg" >&2; exit 1 ;;
  esac
}

image="$(field image)"
version="$(field version)"
platforms=()
while read -r a; do platforms+=("$(platform "$a")"); done < <(arches)
[ "${#platforms[@]}" -gt 0 ] || { echo "No arch list in $cfg" >&2; exit 1; }

case "$cmd" in
  meta)
    echo "image=$image"
    echo "version=$version"
    echo "platforms=$(IFS=,; echo "${platforms[*]}")"
    ;;
  published)
    if ! manifest="$(docker manifest inspect "$image:$version" 2>/dev/null)"; then
      echo "$image:$version: not in registry"
      exit 1
    fi
    # Each manifest entry as os/arch and os/arch/variant, so linux/arm64 matches
    # with or without the "v8" variant buildx sometimes records.
    have="$(jq -r '.manifests[]?.platform | select(.os != "unknown")
                   | (.os + "/" + .architecture), (.os + "/" + .architecture + "/" + (.variant // ""))' <<<"$manifest")"
    for p in "${platforms[@]}"; do
      if ! grep -qxF "$p" <<<"$have"; then
        echo "$image:$version: missing $p"
        exit 1
      fi
    done
    echo "$image:$version: published for ${platforms[*]}"
    ;;
  *)
    echo "Unknown command '$cmd'" >&2
    exit 2
    ;;
esac
