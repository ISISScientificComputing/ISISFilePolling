FROM ghcr.io/isisscientificcomputing/base

USER isisautoreduce
RUN python3 -m pip install --user autoreduce_run_detection==22.0.0.dev1

CMD autoreduce-run-detection
