FROM ghcr.io/autoreduction/base

USER root
RUN mkdir -p /run-detection/
RUN chown isisautoreduce:isisautoreduce /run-detection/
USER isisautoreduce

# Installs run-detection from your local repository
ADD . .
RUN python3 -m pip install --user --no-cache-dir .

CMD autoreduce-run-detection
