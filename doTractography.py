##!/opt/miniconda-latest/bin python3
import argparse
import os
#IXI661-HH-2788
# for the IXI dataset, we do not have a map for inhomogeneities.
# we will use eddy_correct (flirt from fsl), to address it to some extent.
# next versions will include 
# need to include numberof tracks. for now its 10M.
parser = argparse.ArgumentParser(description='perform mrtrix3 based tractography '
                                'on freesurfer parcels.'
                                'For the IXI dataset, we do not have a map for '
                                'deformation fiels. We will stick to eddy_correct'
                                'here. Next versions will include eddy/top-up preprocessing'
                                'as well.')
parser.add_argument('bids_dir', 
                    help='directory based on bids style,'
                         'o/p will be written in ./derivatives/mrtrix/')
parser.add_argument('participant',
                    help='provide participant names completely,'
                         'not just the id 01, 02,.. ',
                    nargs="+")
parser.add_argument('--tracks',
                    help='provide numberof tracts to generate, '
                    'default is 10M')
args = parser.parse_args()
# IXI data requires some processing such as volume merging, and removal of last volume 
# which could be an ADC map. This needs to be done prior to docker. 
# 

write_dv = (args.bids_dir + '/derivatives/mrtrix3')

cmd_1 = ('eddy_correct ' +  args.bids_dir + '/' + \
        args.participant[0] + '/dwi/' + args.participant[0] + '-DTI-merge.nii.gz ' + \
        write_dv + '/' + args.participant[0] + '-DTI-eddy.nii.gz ' + \
        '0')
os.system(cmd_1)

cmd_2 = ('mrconvert -force '  +  write_dv + '/' + args.participant[0] + '-DTI-eddy.nii.gz ' + \
        write_dv + '/' + args.participant[0] + '-DTI.mif -fslgrad ' + \
        args.bids_dir + '/' + args.participant[0] + '/dwi/bvecs.txt ' + \
        args.bids_dir + '/' + args.participant[0] + '/dwi/bvals.txt')
os.system(cmd_2)

cmd_3 = ('dwidenoise -force ' + write_dv + '/' + args.participant[0] + '-DTI.mif ' +\
        write_dv + '/' + args.participant[0] + '-DTI-denoise.mif -noise ' +\
        write_dv + '/' + args.participant[0] + '-DTI-denoise-noise-data.mif ')
os.system(cmd_3)


cmd_4 = ('mrdegibbs -force ' + write_dv + '/' + args.participant[0] + '-DTI-denoise.mif ' + write_dv + '/' + args.participant[0] + '-DTI-denoise-degibbs.mif')
os.system(cmd_4)

cmd_5 = ('dwi2mask -force ' + write_dv + '/' + args.participant[0] + '-DTI-denoise-degibbs.mif ' + write_dv + '/' + args.participant[0] + '-DTI-mask.mif')
os.system(cmd_5)

cmd_6 = ('dwi2response tournier ' +  write_dv + '/' + args.participant[0] + '-DTI-denoise-degibbs.mif ' + \
          write_dv + '/' + args.participant[0] + '-DTI-response.mif')
os.system(cmd_6)

cmd_7 =('dwi2fod csd ' + write_dv + '/' + args.participant[0] + '-DTI-denoise-degibbs.mif -mask ' + \
        write_dv + '/' + args.participant[0] + '-DTI-mask.mif ' + \
        write_dv + '/' + args.participant[0] + '-DTI-response.mif ' + \
        write_dv + '/' + args.participant[0] + '-DTI-fod.mif')
os.system(cmd_7)

cmd_8 = ('mrconvert ' +  args.bids_dir + '/' + args.participant[0] + '/anat/' + args.participant[0] + '-T1.nii.gz ' + \
         write_dv + '/' + args.participant[0] + '-T1.mif')
os.system(cmd_8)

cmd_9 = ('5ttgen fsl ' +  write_dv + '/' + args.participant[0] + '-T1.mif ' + \
        write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg.mif')
os.system(cmd_9)

cmd_10 = ('dwiextract ' + write_dv + '/' + args.participant[0] + '-DTI-denoise-degibbs.mif -bzero ' + \
          write_dv + '/' + args.participant[0] + '-DTI-b0-extracted.mif')
os.system(cmd_10)      

cmd_11 = ('mrmath ' + write_dv + '/' + args.participant[0] + '-DTI-b0-extracted.mif mean ' + \
        write_dv + '/' + args.participant[0] + '-DTI-b0-extracted_mean.mif -axis 3')
os.system(cmd_11)

cmd_12 = ('mrconvert ' + write_dv + '/' + args.participant[0] + '-DTI-b0-extracted_mean.mif ' + \
        write_dv + '/' + args.participant[0] + '-DTI-b0-extracted_mean.nii.gz')
os.system(cmd_12)

cmd_13 = ('mrconvert ' + write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg.mif ' + write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg.nii.gz')
os.system(cmd_13)

cmd_14 = ('fslroi ' + write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg.nii.gz ' + \
         write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg-vol0.nii.gz 0 1')
os.system(cmd_14)

cmd_15 = ('flirt -in ' + write_dv + '/' + args.participant[0] + '-DTI-b0-extracted_mean.nii.gz -ref ' + \
         write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg-vol0.nii.gz -interp nearestneighbour -dof 6 -omat ' + \
         write_dv + '/' + args.participant[0] + '-diif2struct_fsl.mat')
os.system(cmd_15)

cmd_16 = ('transformconvert ' + write_dv + '/' + args.participant[0] + '-diif2struct_fsl.mat  ' + \
         write_dv + '/' + args.participant[0] + '-DTI-b0-extracted_mean.nii.gz ' + \
         write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg.nii.gz flirt_import ' + \
         write_dv + '/' + args.participant[0] + '-diff2struct-matrix.txt')

os.system(cmd_16)
cmd_17 = ('mrtransform ' + write_dv + '/' + args.participant[0] + '-T1-5tt-nocoreg.mif -linear ' + \
         write_dv + '/' + args.participant[0] + '-diff2struct-matrix.txt -inverse ' + \
         write_dv + '/' + args.participant[0] + '-T1-5tt-coreg.mif' )
os.system(cmd_17)

cmd_18 = ('5tt2gmwmi ' + write_dv + '/' + args.participant[0] + '-T1-5tt-coreg.mif ' + \
         write_dv + '/' + args.participant[0] + '-gmwmSeed-coreg.mif')
os.system(cmd_18)

# mention threads - mentioned tract samples. default is 10M here.
cmd_19 = ('tckgen -force -act ' + write_dv + '/' + args.participant[0] + '-T1-5tt-coreg.mif -backtrack -seed_gmwmi ' +  write_dv + '/' + args.participant[0] + '-gmwmSeed-coreg.mif ' + \
        '-nthreads 64 -maxlength 250 -cutoff 0.06 -select ' + '10M ' + \
         write_dv + '/' + args.participant[0] + '-DTI-fod.mif ' + \
         write_dv + '/' + args.participant[0] + '-' + '.tck')
os.system(cmd_19)

# mention threads
cmd_20 = ('tcksift2 -force -act ' + write_dv + '/' + args.participant[0] + '-T1-5tt-coreg.mif -out_mu ' + write_dv + '/' + args.participant[0] + '-sift_mu.txt -out_coeffs ' + \
        write_dv + '/' + args.participant[0] + '-sift_coeffs.txt -nthreads 64 ' + \
        write_dv + '/' + args.participant[0] + '-' + '.tck ' + \
        write_dv + '/' + args.participant[0] + '-DTI-fod.mif ' + write_dv + '/' + args.participant[0] + '-sift.txt')
os.system(cmd_20)         

cmd_21 = ('labelconvert ' + args.bids_dir + '/derivatives/freesurfer/' + args.participant[0] + '-T1_aparc_aseg.mgz ' + \
         '/opt/freesurfer-7.1.1-min/FreeSurferColorLUT.txt ' + '/opt/mrtrix3-3.0.2/share/mrtrix3/labelconvert/fs_default.txt ' + \
         write_dv + '/' + args.participant[0] + '-T1-parcels.mif')
os.system(cmd_21)

cmd_22 = ('mrtransform -force ' + write_dv + '/' + args.participant[0] + '-T1-parcels.mif -interp nearest -linear ' + write_dv + '/' + args.participant[0] + '-diff2struct-matrix.txt ' + \
        '-inverse -datatype uint32 ' + write_dv + '/' + args.participant[0] + '-T1-parcels-coreg.mif')
os.system(cmd_22)

cmd_23 = ('tck2connectome -symmetric -zero_diagonal -scale_invnodevol -tck_weights_in ' \
         + write_dv + '/' + args.participant[0] + '-sift.txt ' + \
         write_dv + '/' + args.participant[0] + '-' + '.tck ' + \
         write_dv + '/' + args.participant[0] + '-T1-parcels-coreg.mif ' + \
         write_dv + '/' + args.participant[0] + '-connectome.csv -out_assignment ' + \
         write_dv + '/' + args.participant[0] + '-connectome2tract.csv')
os.system(cmd_23)
