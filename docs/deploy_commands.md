# Activate the virtual environment and navigate to the project directory
PC:    source ~/python/SZTAKI_robojudo_311/bin/activate
ROBOT: source ~/python/SZTAKI_robojudo_311/bin/activate
cd code/Robojudo....

# sim2sim: 
python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker  --motion-path assets/motions/g1/_.pt --motion-index 0

# sim2real:
python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker_real  --motion-path assets/motions/g1/_.pt --motion-index 0

# Custom motion library:
python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker  --motion-path assets/motions/g1/g1_bones_seed_selection.pt --motion-index 0