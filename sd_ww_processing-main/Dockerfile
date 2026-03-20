FROM condaforge/miniforge3:25.3.1-0

RUN apt update &&\
apt install -yy parallel rename git vim

RUN mamba create --name freyja python=3.11 &&\
conda config --add channels bioconda &&\
conda config --add channels conda-forge

RUN mamba run -n freyja mamba install -n freyja freyja=2.0.1  -y


COPY ./demix_parallel_ubuntu.sh /app/demix_parallel_ubuntu.sh
COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/demix_parallel_ubuntu.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
