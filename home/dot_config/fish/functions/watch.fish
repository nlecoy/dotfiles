function watch --description 'watch with fish alias support'
    if test (count $argv) -eq 0
        echo "usage: watch COMMAND [ARGS...]" >&2
        return 1
    end
    if command -q viddy
        command viddy --disable_auto_save --differences --interval 2 --shell fish -- $argv
    else
        command watch -x fish -c "(string escape -- $argv)"
    end
end
