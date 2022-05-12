FROM ghcr.io/autoreduction/base

# Env var for data directory of run-detection (e.g. where last_runs.csv is stored)
ENV AUTOREDUCTION_USERDIR=/run-detection/

USER root
RUN mkdir -p ${AUTOREDUCTION_USERDIR}
RUN chown isisautoreduce:isisautoreduce ${AUTOREDUCTION_USERDIR}
USER isisautoreduce

# Installs run-detection from your local repository
ADD . .
RUN python3 -m pip install --user --no-cache-dir .

CMD autoreduce-run-detection
