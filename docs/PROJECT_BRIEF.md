        # Project Brief

        shellexpand exists to solve a narrow, inspectable developer-tooling problem:
        Zero-dep POSIX-style shell text expansion: tilde, brace, parameter ($VAR, ${VAR:-d}), escape handling, clean error tree.

        ## Portfolio Role

        This repository is part of the local-first engineering portfolio around
        agentic AI infrastructure, evaluation, parsing, safety boundaries, and
        small tools that can be understood from a fresh source checkout. It is not
        here to inflate repository count; it should either provide a reusable
        primitive, a benchmark surface, or a concrete local workflow.

        Topics: brace-expansion, expansion, python, shell, zero-dependencies

        ## Current Gates

        - Latest completed CI: success
        - Source files counted by audit: 7
        - Test files counted by audit: 8
        - Latest release: not release-tracked yet
        - License: MIT

        ## Upgrade Path

        - Add golden-output fixtures for narrow terminals, Unicode width, and ANSI escape handling.
- Document compatibility with pipes, files, and non-interactive shells.
- Add performance notes for large inputs and streaming behavior where applicable.

        ## Reviewer Contract

        A serious reviewer should be able to clone the repository, read the
        README and this brief, run the tests, and understand exactly what is
        claimed. Future work should prefer deeper correctness, better fixtures,
        clearer limits, and stronger local demos over broad feature lists.
