FROM ghcr.io/autoreduction/base

USER root
RUN mkdir -p /run-detection/
RUN chown isisautoreduce:isisautoreduce /run-detection/
USER isisautoreduce

# Installs run-detection from your local repository
ADD . .
RUN python3 -m pip install --user --no-cache-dir .

# Uncomment below if you want to install from pypi
# add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple for packages in test.pypi.org
# RUN python3 -m pip install --user --no-cache-dir autoreduce_run_detection==22.0.0.dev7

CMD autoreduce-run-detection
