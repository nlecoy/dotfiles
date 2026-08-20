if test (uname) = Darwin
    set -gx PNPM_HOME $HOME/Library/pnpm
else
    set -gx PNPM_HOME $HOME/.local/share/pnpm
end

fish_add_path --global $PNPM_HOME
fish_add_path --global $PNPM_HOME/bin
