#!/bin/bash

eval "$(mamba shell hook --shell bash)"
mamba activate freyja
exec /app/demix_parallel_ubuntu.sh /data # Mount directory at /data
