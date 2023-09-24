@echo off

cd %cd%

java -ea -Dlog-viewer.config-file=%cd%/config.conf -jar %cd%/lib/log-viewer-cli-1.0.6.jar startup
