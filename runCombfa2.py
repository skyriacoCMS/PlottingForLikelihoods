import os
import sys



cmnd = "combine --robustFit=0 --algo grid --floatOtherPOIs=0 --alignEdges=1 -P CMS_zz4l_fai2  --saveSpecifiedFunc=CMS_zz4l_fai1,CMS_zz4l_fai2,CMS_zz4l_fai3_relative,CMS_zz4l_fai3,CMS_zz4l_fai1,CMS_zz4l_fai2  --saveInactivePOI=1 --X-rtd OPTIMIZE_BOUNDS=0 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_MaxCalls=999999999 -t -1  -V -v 3 --saveNLL  -M MultiDimFit -m 125 -d scanfa3_2016.root --points 301  --setParameterRanges CMS_zz4l_fai2=-1,1 "
os.system(cmnd)
os.system("mv higgsCombineTest.MultiDimFit.mH125.root  higgs_fullrange.root")

cmnd = "combine --robustFit=0 --algo grid --floatOtherPOIs=0 --alignEdges=1 -P CMS_zz4l_fai2  --saveSpecifiedFunc=CMS_zz4l_fai1,CMS_zz4l_fai2,CMS_zz4l_fai3_relative,CMS_zz4l_fai3,CMS_zz4l_fai1,CMS_zz4l_fai2  --saveInactivePOI=1 --X-rtd OPTIMIZE_BOUNDS=0 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_MaxCalls=999999999 -t -1  -V -v 3 --saveNLL  -M MultiDimFit -m 125 -d scanfa3_2016.root --points 101  --setParameterRanges CMS_zz4l_fai2=-0.02,0.02 "
os.system(cmnd)
os.system("mv higgsCombineTest.MultiDimFit.mH125.root  higgs_zoom.root")

os.system("hadd -f -k  higgs_fa2.root higgs_zoom.root higgs_fullrange.root")

