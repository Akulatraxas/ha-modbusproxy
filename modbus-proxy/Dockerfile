ARG BUILD_FROM
FROM $BUILD_FROM

# Install python + pip
RUN \
  apk add --no-cache \
    python3 py3-pip py3-yaml

# Install modbus + py3yaml via pip
RUN pip install modbus-proxy

# Copy data for add-on
WORKDIR /
COPY run.sh /
COPY rootfs /
WORKDIR /srv



RUN chmod a+x /run.sh
CMD [ "/run.sh" ]