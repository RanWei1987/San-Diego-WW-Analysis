# sd_ww_processing
repo for data storage and shared analyses

Repository for dashboard is at [andersen-lab/SARS-CoV-2_WasteWater_San-Diego](https://github.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego).

## Instructions


Set number of parallel jobs to run in `demix_parallel_ubuntu.sh`. Default is set to `30`.

To run use the docker container,

```
docker build -t condaforge/miniforge3:freyja-2.0.0 .
docker run -v $(pwd):/data condaforge/miniforge3:freyja-2.0.0
```
