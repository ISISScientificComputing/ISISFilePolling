FROM ghcr.io/autoreduction/base

USER isisautoreduce
RUN python3 -m pip install --user autoreduce_run_detection==22.0.0.dev8

CMD autoreduce-run-detection
