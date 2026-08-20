function listening --description 'List processes listening on TCP ports'
    if test (count $argv) -eq 0
        lsof -iTCP -sTCP:LISTEN -n -P
    else if test (count $argv) -eq 1
        lsof -iTCP -sTCP:LISTEN -n -P | grep -i --color $argv[1]
    else
        echo "Usage: listening [pattern]"
        echo "(you may want to use sudo here!)"
    end
end
