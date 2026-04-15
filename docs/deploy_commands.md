
source ~/python/SZTAKI.../bin/activate

cd code/Robojudo....

# sim2sim: 

python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker  --motion-path assets/motions/g1/g1_3steps.50fps.pt --motion-index 0

# sim2real:

python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker_real  --motion-path assets/motions/g1/g1_3steps.50fps.pt

# Tried motions: 
python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker  --motion-path assets/motions/g1/g1_bones_seed_mini.pt --motion-index 49

- 49 dance
- 19 slow walk
