FROM ghcr.io/isisscientificcomputing/base

USER isisautoreduce
RUN python3 -m pip install --user autoreduce_run_detection==22.0.0.dev0

CMD python3 -m autoreduce_run_detection.run_detection
