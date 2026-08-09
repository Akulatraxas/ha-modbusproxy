#!/usr/bin/with-contenv bashio

set +x

CONFIG_FILE=./modbus.config.yaml

CONFIG_TIMEOUT=$(bashio::config 'timeout' '10')
CONFIG_CONNECTIONTIME=$(bashio::config 'connection_time' '0')
CONFIG_LOGLEVEL=$(bashio::config 'loglevel' 'INFO')

echo "Preparing to run modbus-proxy"

echo "devices:" > "${CONFIG_FILE}"

add_device() {
    local host=$1
    local port=$2
    local listen=$3
    local timeout=$4
    local connection_time=$5

    echo "Device: ${host}:${port} -> listening on 0:${listen} (timeout: ${timeout}s, connection_time: ${connection_time}s)"

    cat >> "${CONFIG_FILE}" <<EOF
  - modbus:
      url: ${host}:${port}
      timeout: ${timeout}
      connection_time: ${connection_time}
    listen:
      bind: 0:${listen}
EOF
}

if bashio::config.has_value 'devices'; then
    for i in $(bashio::config 'devices|keys'); do
        DEVICE_HOST=$(bashio::config "devices[${i}].upstreamhost")
        DEVICE_PORT=$(bashio::config "devices[${i}].upstreamport")
        DEVICE_LISTEN=$(bashio::config "devices[${i}].listenport")
        DEVICE_TIMEOUT=$(bashio::config "devices[${i}].timeout" "${CONFIG_TIMEOUT}")
        DEVICE_CONNECTIONTIME=$(bashio::config "devices[${i}].connection_time" "${CONFIG_CONNECTIONTIME}")
        add_device "${DEVICE_HOST}" "${DEVICE_PORT}" "${DEVICE_LISTEN}" "${DEVICE_TIMEOUT}" "${DEVICE_CONNECTIONTIME}"
    done
else
    CONFIG_HOST=$(bashio::config 'upstreamhost')
    CONFIG_PORT=$(bashio::config 'upstreamport')
    CONFIG_LISTENPORT=$(bashio::config 'listenport')
    add_device "${CONFIG_HOST}" "${CONFIG_PORT}" "${CONFIG_LISTENPORT}" "${CONFIG_TIMEOUT}" "${CONFIG_CONNECTIONTIME}"
fi

cat >> "${CONFIG_FILE}" <<EOF
logging:
  version: 1
  formatters:
    standard:
      format: "%(asctime)s %(levelname)8s %(name)s: %(message)s"
  handlers:
    console:
      class: logging.StreamHandler
      formatter: standard
  root:
    handlers: ['console']
    level: ${CONFIG_LOGLEVEL}
EOF

echo "Generated Config"
cat "${CONFIG_FILE}"

if [ -f "./venv/bin/activate" ] ; then
    source ./venv/bin/activate
fi
modbus-proxy -c "${CONFIG_FILE}"
