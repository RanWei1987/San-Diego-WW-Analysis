@echo off
REM Works with Docker image: condaforge/miniforge3:23.11.0-0

pushd .

REM Get arguments
set "terra_workspace=%~1"
set "terra_table=%~2"
set "prefix=%~3"
set "dump_folder=%~4"

REM Get the table from Terra

REM Change directory to prefix

echo Started


 
call terraTools\Scripts\activate


python "packages\terra-tools-master\scripts\export_large_tsv\export_large_tsv.py" --project cdph-terrabio-taborda-manual --workspace "%terra_workspace%" --entity_type "%terra_table%" --tsv %terra_table%.tsv"

call deactivate
call conda activate wastewater

move "%terra_table%.tsv" "%prefix%"

cd /d "%prefix%"

python cloud_download.py "%terra_table%.tsv" "%dump_folder%" "freyja_demixed"
dir
echo Finished

setlocal enabledelayedexpansion

for %%F in (%dump_folder%\*demixed.tsv) do (
    rem --- Check if filename contains Neg or Pos ---
    echo %%~nxF | findstr /i "Neg Pos" >nul
    set "err=!errorlevel!"
    if !err! EQU 0 (
        echo Skipping ^(Neg or Pos found^): %%~nxF
    ) else (
        rem --- Check if filename contains SC2 ---
        echo %%~nxF | findstr /i "SC2" >nul
        set "err2=!errorlevel!"
        if !err2! EQU 0 (
            copy "%%F" ".\outputs\"
            echo Copied: %%~nxF
        ) else (
            echo Skipping ^(not SC2^): %%~nxF
        )
    )
)

endlocal

REM -------------------------------
REM Rename files in variants folder
cd variants
REM rename 1.tsv to 1.variants.tsv and *1.tsv
REM for %%f in (*1.tsv) do (
REM    set "filename=%%~nf"
REM    if "%%~xf"==".tsv" ren "%%f" "%%filename%.variants.tsv"
REM )
cd ..

REM Rename depth files
REM cd depths
REM for %%f in (*depths.txt) do (
REM     set "filename=%%~nf"
REM    ren "%%f" "%%filename:.depths=.depth%"
REM )
REM cd ..

REM Update Freyja
REM freyja update --outdir .
REM freyja update
REM Freyja cannot run under Windows system. So we manually refresh the lineages structure meta file

curl https://raw.githubusercontent.com/andersen-lab/Freyja/main/freyja/data/lineages.yml -o lineages.yml


REM -------------------------------
REM Define function as a subroutine
REM Usage: call :my_func "variant_file" "depthfolder" "outputfolder"
REM :my_func
REM set "fn=%~1"
REM set "depthfolder=%~2"
REM set "output=%~3"

REM Get filename without path
REM for %%F in ("%fn%") do set "fn_out=%%~nxF" & set "baseName=%%~nF"

REM set "depthfile0=%depthfolder%%baseName%.depth"
REM set "output0=%output%%baseName%.demix.tsv"

REM echo Processing %fn%
REM echo Depth file: %depthfile0%
REM echo Output file: %output0%

REM freyja demix "%fn%" "%depthfile0%" --output "%output0%" --eps 0.0000001 --autoadapt
REM goto :eof

REM -------------------------------
REM Example: loop through variant files
REM This replaces the GNU parallel call
REM Adjust paths as needed
REM for %%F in (variants\*_25_*) do (
REM     call :my_func "%%F" "depths\" "outputs\"
REM )


REM Aggregate outputs, use a wrapper to call freyja aggregate in win64
REM freyja aggregate outputs\ --output agg_outputs.tsv
python aggregate_wrapper.py outputs/ agg_outputs.tsv
echo Finished


REM Run Python scripts
python polish_outputs_SD.py
echo FinallyFinished
REM python calc_relgrowthrates.py
popd
call conda deactivate