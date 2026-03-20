#!/bin/bash

# Works with Docker image: condaforge/miniforge3:23.11.0-0

prefix=$1
cd $1/

# for uniform naming
cd variants/
# rename 1.tsv 1.variants.tsv *1.tsv
rename 's/1\.tsv$/1.variants.tsv/' *1.tsv
cd ../depths/
# rename _depths.txt .depth *_depths.txt
rename 's/depths\.txt$/.depth/' *depths.txt
cd ..
freyja update --outdir . 
freyja update

my_func() {
    fn=$1
    depthfolder=$2
    output=$3

    fn_out=${fn##*/}
    baseName=${fn##*/}
    baseName=${baseName%.*}
    depthfile0="${depthfolder}${fn_out%.variants.tsv}.depth"
    output0="${output}${fn_out%.*}.demix.tsv"
    echo $fn
    echo $depthfile0
    echo $output0
    freyja demix $fn $depthfile0 --output $output0 --eps 0.0000001 --autoadapt

}

export -f my_func
export SHELL=/bin/bash
export RAYON_NUM_THREADS=1 # Limit number of threads to 1

parallel --env RAYON_NUM_THREADS --env my_func -j 30 my_func {} depths/ outputs/ ::: variants/*_25_*

freyja aggregate outputs/ --output agg_outputs.tsv

python polish_outputs.py
python calc_relgrowthrates.py
