# Podman Desktop installs the CLI in /opt/podman/bin without a symlink in /usr/local/bin
if test -d /opt/podman/bin
    fish_add_path --global /opt/podman/bin
end
