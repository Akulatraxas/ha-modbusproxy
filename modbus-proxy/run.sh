#!/usr/bin/with-contenv bashio

set +x

# Create main config
CONFIG_HOST=$(bashio::config 'upstreamhost')
CONFIG_PORT=$(bashio::config 'upstreamport')
CONFIG_LISTENPORT=$(bashio::config 'listenport')
CONFIG_TIMEOUT=$(bashio::config 'timeout')
CONFIG_CONNECTIONTIME=$(bashio::config 'connection_time')
CONFIG_LOGLEVEL=$(bashio::config 'loglevel')


echo "Preparing to run modbus-proxy"
echo "Upstream: $CONFIG_HOST:$CONFIG_PORT"
echo "Listen: $CONFIG_LISTENPORT"
echo "Timeout: $CONFIG_TIMEOUT"
echo "Connection Time: $CONFIG_CONNECTIONTIME"
echo "Loglevel: $CONFIG_LOGLEVEL"

sed -i "s/__HOST__/${CONFIG_HOST}/g" ./modbus.config.yaml
sed -i "s/__PORT__/${CONFIG_PORT}/g" ./modbus.config.yaml
sed -i "s/__LISTENPORT__/${CONFIG_LISTENPORT}/g" ./modbus.config.yaml
sed -i "s/__TIMEOUT__/${CONFIG_TIMEOUT}/g" ./modbus.config.yaml
sed -i "s/__CONNECTIONTIME__/${CONFIG_CONNECTIONTIME}/g" ./modbus.config.yaml
sed -i "s/__LOGLEVEL__/${CONFIG_LOGLEVEL}/g" ./modbus.config.yaml

echo "Generated Config"
cat ./modbus.config.yaml

if [ -f "./venv/bin/activate" ] ; then
    source ./venv/bin/activate
fi
modbus-proxy -c ./modbus.config.yaml