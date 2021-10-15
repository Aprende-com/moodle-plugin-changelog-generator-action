#!/usr/bin/env python3

from git import Repo
from re import compile as regex_compile
from os import environ as ENV
from argparse import ArgumentParser

# Angular Convention Types:
# References:
# https://www.conventionalcommits.org/en/v1.0.0/
# https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines
CONVENTION_TYPES = {
        "build": "Build",  # Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
        "ci": "CI",        # Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
        "feat": "Features",  # A new feature
        "fix": "Fixes",      # A bug fix
        "perf": "Performance",   # A code change that improves performance
        "refactor": "Refactor",  # A code change that neither fixes a bug nor adds a feature
        "style": "Styles",       # Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
        "test": "Tests"          # Adding missing tests or correcting existing tests
        # "docs:": "Documentation",   # Documentation only changes
        #                               NOT USED HERE TO PREVENT AUTO
        #                               GENERATED COMMENTS FOR DOCS
}


def main():
    """ Creates a changelog file based on the commits messages. """

    ap = ArgumentParser(description=main.__doc__)

    ap.add_argument('-p', '--path', type=str,
                    default=ENV.get('INPUT_PATH'))
    ap.add_argument('-f', '--filename', type=str,
                    default=ENV.get('INPUT_FILENAME'))

    ap.add_argument('-d', '--debug', action='store_true',
                    default=False)
    ap.add_argument('-z', '--dry-run', action='store_true',
                    default=False)

    args = ap.parse_args()
    print(args)  # Debug

    print(f"Analizing git repository at: {args.path}")
    repo = Repo(args.path)

    if repo.bare:
        raise Exception("Bare repo found!")

    regex_expression = r'^(build:|ci:|feat:|fix:|perf:|refactor:|style:|test:)'
    regex = regex_compile(regex_expression)

    commits = [commit_json(x) for x in repo.iter_commits()
               if regex.findall(x.message)]
    commits_dict = commits_to_dict(commits)

    output = ['# Changelog']
    for date in commits_dict.keys():
        output.append(f"## {date}")

        for commit_type in CONVENTION_TYPES:
            if commit_type in commits_dict[date]:
                output.append(f"### {CONVENTION_TYPES[commit_type]}")
                for commit in commits_dict[date][commit_type]:
                    output.append(commit_line(repo, commit))

    if not args.dry_run:
        if len(output) > 1:
            output_filename = f"{args.path}/{args.filename}"
            with open(output_filename, "w+") as file:
                file.writelines([ f"{x}\n" for x in output])
            print(f"{output_filename} written")
        else:
            print("No matching commits found :'(")

    if args.debug and len(output) > 1:
        [print(x.rstrip()) for x in output]


def commit_json(commit):
    return {
        'sha': commit.hexsha,
        'type': commit.message.split(': ')[0],
#        'message': commit.message.split(': ')[1].rstrip(),
        'message': commit.message.rstrip(),
        'date': commit.committed_datetime.strftime('%Y-%m-%d'),
        'author': commit.author
    }


def commit_line(repo, commit):
    short_sha = repo.git.rev_parse(commit['sha'], short=8)
    link = f"../../commit/{short_sha}"
    message_first_line = commit['message'].split('\n')[0].split("{commit['type']}: ")[1]
    return f"* {message_first_line} by **@{commit['author']}** in [{short_sha}]({link})"


def commits_to_dict(commits):
    commits_dict = {}
    for commit in commits:
        if commit['date'] not in commits_dict:
            commits_dict[commit['date']] = {}
        if commit['type'] not in commits_dict[commit['date']]:
            commits_dict[commit['date']][commit['type']] = []
        commits_dict[commit['date']][commit['type']].append(commit)
    return commits_dict


if __name__ == "__main__":
    main()
