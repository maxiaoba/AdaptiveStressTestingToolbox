source ~/scratch/miniconda3/etc/profile.d/conda.sh
conda activate AST
cd ..
unset PYTHONPATH
export PYTHONPATH=$(pwd):$(pwd)/garage/src:$PYTHONPATH
cd ../..
charm AdaptiveStressTestingToolbox
