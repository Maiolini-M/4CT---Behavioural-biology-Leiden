# Pyhton script for the GUI of the 4 choice experiment

The app should control the 4 speakers (1, 2, 3, 4) in the setup and play different songs (A, B, C, D). With a combobox you select the starting position associated for each song to each speakers. While with a spinbox you select the timeout period that the microswitch's perch have to count an occurence.

In the Switching section you control the switch of the association between speakers and song selected (i.e. A-2, B-3, C-4, D-1 means Song A in speaker 2, song B in speaker 3, song C in speaker 4 and song D in speaker 1), the time of this position, so from start time to end time.
You can have maximum 6 switch in an experiment.

When pressing start each song are associated with a speaker and a perch. When the bird activate the microswitch on the perch (by sitting or hopping) in the log should be registered the count and in which speaker is placed.

![Logic_scheme]()

## Update on the script
*Maiolini Marco, 12/06*

I have programmed the basic function, but as I never programmed something from an input I didn't done the perch timout function and the switch function yet.
