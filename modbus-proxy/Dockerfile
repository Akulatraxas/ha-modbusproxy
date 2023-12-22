ARG BUILD_FROM
FROM $BUILD_FROM

# Install python + pip
WORKDIR /srv
RUN \
  apk add --no-cache \
    python3 py3-pip py3-yaml

# Prepare venv
RUN cd /srv && python3 -m venv venv

# Install modbus + py3yaml via pip
RUN cd /srv && source ./venv/bin/activate && \
    pip install modbus-proxy


# Copy data for add-on
WORKDIR /
COPY run.sh /
COPY rootfs /
WORKDIR /srv



RUN chmod a+x /run.sh
CMD [ "/run.sh" ]