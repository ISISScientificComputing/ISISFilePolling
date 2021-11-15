FROM autoreduction/base

USER isisautoreduce
RUN python3 -m pip install --user autoreduce_run_detection.run_detection

CMD python3 -m autoreduce_run_detection.run_detection
