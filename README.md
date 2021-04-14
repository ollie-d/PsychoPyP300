# PsychoPyP300
Simple PsychoPy visual oddball paradigm. Designed to be a test of LSL marker and photosensor latency.
<br><br>
Use provided conda environment to make sure everything runs correctly. Run this in a conda terminal:<br>
```conda env create -n psychopy3 -f conda_env.yml```
<br><br>
After activating, just run paradigm via<br>
```python visual_oddball.py```
<br><br>
There's a 5 second delay at the start to ensure the LSL stream is started before the task starts. All other timing is based off frames so make sure the refresh_rate variable is set correctly!
<br><br>
Paradigm based off Li et al., 2019: <br>
https://www.frontiersin.org/articles/10.3389/fnhum.2018.00520/full
