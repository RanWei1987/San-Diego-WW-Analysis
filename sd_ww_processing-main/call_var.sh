#!/bin/bash
my_func() {
    fn=$1
    varfolder=$2
    depthfolder=$3

    fn_out=${fn##*/}
    # echo $fn
    # echo $fn_out
    # echo $varfolder
    # echo $depthfolder
    baseName=${fn##*/}
    baseName=${baseName%.*}
    # echo $depthfolder$baseName
    depthfile0="${depthfolder}${fn_out%.*}.depth"
    varfile0="${varfolder}${fn_out%.*}.variants.tsv"
    # echo $depthfile0
    echo $fn
    if [ -e $varfile0 ]
    then
        echo "${varfile0} exists"
    else
        echo "${varfile0} does not exist"
        freyja variants $fn --variants $varfile0 --depths $depthfile0 --ref NC_045512_Hu-1.fasta
    fi 
}

export -f my_func
parallel -j 8 my_func ::: bams/* ::: variants/ ::: depths/