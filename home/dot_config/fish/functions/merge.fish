function merge --description "Squash-merge every open PR of a repo and delete the branch"
    argparse --name=gh-merge-all 'R/repo=' 'a/author=' 'L/limit=' 'auto' 'admin' 'n/dry-run' -- $argv
    or return

    set -l repo_args
    test -n "$_flag_repo"; and set repo_args --repo $_flag_repo

    set -l author_args
    test -n "$_flag_author"; and set author_args --author $_flag_author

    set -l limit 100
    test -n "$_flag_limit"; and set limit $_flag_limit

    set -l merge_args --squash --delete-branch
    set -q _flag_auto; and set -a merge_args --auto
    set -q _flag_admin; and set -a merge_args --admin

    set -l prs (gh pr list $repo_args $author_args --state open --limit $limit \
        --json number --jq '.[].number')
    or return $status

    if test (count $prs) -eq 0
        echo "no open pull request"
        return 0
    end

    if set -q _flag_dry_run
        printf 'would squash-merge #%s\n' $prs
        return 0
    end

    set -l failed
    for n in $prs
        echo "==> merging #$n"
        if not gh pr merge $n $repo_args $merge_args
            set -a failed $n
        end
    end

    if test (count $failed) -gt 0
        printf 'failed: #%s\n' $failed >&2
        return 1
    end
end
