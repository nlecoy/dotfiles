#!/bin/bash

# Format a token count as a compact value (e.g. 200000 -> 200k, 1000000 -> 1M)
format_tokens() {
  local tokens="$1"
  if [ "$tokens" -ge 1000000 ]; then
    local millions
    millions=$(echo "scale=1; $tokens / 1000000" | bc -l 2>/dev/null || echo "1")
    case "$millions" in
    *.0) millions=${millions%.0} ;;
    esac
    printf "%sM" "$millions"
  else
    printf "%dk" "$((tokens / 1000))"
  fi
}

# Main
main() {
  # Read JSON from stdin
  local json_input
  json_input=$(cat)

  # Extract model and context-window info (Claude Code provides these directly)
  local model capacity used_percent used_tokens
  model=$(echo "$json_input" | jq -r '.model.display_name // .model // "unknown"' 2>/dev/null)
  capacity=$(echo "$json_input" | jq -r '.context_window.context_window_size // 200000' 2>/dev/null)
  used_percent=$(echo "$json_input" | jq -r '.context_window.used_percentage // 0' 2>/dev/null)
  used_tokens=$(echo "$json_input" | jq -r '.context_window.total_input_tokens // 0' 2>/dev/null)

  # Round percentage to one decimal
  used_percent=$(printf "%.1f" "$used_percent" 2>/dev/null || echo "0.0")

  # Output status line
  printf "🤖 %s | 📊 %s%% (%s/%s)\n" \
    "$model" "$used_percent" "$(format_tokens "$used_tokens")" "$(format_tokens "$capacity")"
}

main "$@"
