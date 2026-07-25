set -gx KUBE_EDITOR nvim
set -gx VISUAL nvim
set -gx EDITOR nvim
set -gx GOPATH $HOME/.go
set -gx PY_COLORS true
set -gx LANG en_US.utf-8

status is-interactive; and set -gx GPG_TTY (tty)

fish_add_path --global $HOME/.local/bin
fish_add_path --global $HOME/.cargo/bin
fish_add_path --global $HOME/.krew/bin
fish_add_path --global $HOME/.go/bin
