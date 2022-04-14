#!/usr/bin/with-contenv bashio

# Create main config
CONFIG_HOST=$(bashio::config 'upstreamhost')
CONFIG_PORT=$(bashio::config 'upstreamport')
CONFIG_LISTENPORT=$(bashio::config 'listenport')

echo "Preparing to run modbus-proxy"
echo "Upstream: $CONFIG_HOST:$CONFIG_PORT"
echo "Listen: $CONFIG_LISTENPORT"

sed -i "s/__HOST__/${CONFIG_HOST}/g" ./modbus.config.yaml
sed -i "s/__PORT__/${CONFIG_PORT}/g" ./modbus.config.yaml
sed -i "s/__LISTENPORT__/${CONFIG_LISTENPORT}/g" ./modbus.config.yaml

cat ./modbus.config.yaml

echo $PWD
ls -la .

modbus-proxy -c ./modbus.config.yaml