#
#neurodocker generate Singularity \
#    --pkg-manager apt \
#    --base-image debian:buster-slim \
#    --miniconda version=latest\
#    --fsl version=5.0.10 \
#    --freesurfer version=7.1.1-min \
#    --ants version=2.3.4 \
#    --mrtrix3 version=3.0.2 \
#> Singularity

docker build -t neuro_tools:ver0.2 .
