# Guideline 4CT app

## What is the software doing?

This software is designed for four-way operant preference tests in which birds can trigger sound playback through individual speakers by hopping on specific perches. Such acoustic preference tests can be used to investigate whether variation in an acoustic signal affects its attractiveness (for a review on acoustic preference testing methods see Riebel, 2017). The number of times that a bird triggers a specific sound relative to the other sounds in the test is typically used as a measure of the relative attractiveness of that sound. Using pre-recorded stimuli rather than live vocalizing individuals offers a much higher level of stimulus control and in zebra finches, a female’s preference in an operant acoustic test was found to be consistent with her preference in a test with live males (Holveck & Riebel, 2007), suggesting this is a valid method for testing how attractive different sounds are to birds. It is important to note, however, that the spatial arrangement of the presented sounds can bias a bird’s behaviour in the task and should therefore be carefully considered. A previously published four-way acoustic operant preference test with zebra finches used a circular set-up in which all operant perches were equidistant from each other and from the center of the set-up (Wei et al., 2022). 

### References
1. Riebel, K. (2017). Acoustic preference methods: assessing mates. In C. Brown & T. Riede (Eds.), Comparative Bioacoustics: An overview (pp. 253-201). Bentham Books. https://doi.org/10.2174/9781681083179117010009
2. Holveck, M. J., & Riebel, K. (2007). Preferred songs predict preferred males: consistency and repeatability of zebra finch females across three test contexts. Animal Behaviour, 74(2), 297–309. https://doi.org/10.1016/j.anbehav.2006.08.016
3. Wei, J., Liu, Q., & Riebel, K. (2022). Generalisation of early learned tutor song preferences in female zebra finches (Taeniopygia guttata). Behavioural Processes, 201, 104731

## How does it work?
Screenshot of the user interface can be found below (fig. 1). 
The program allows the user to play sounds from four individual speakers. Sound playbacks are triggered by a bird landing on a perch in front of a speaker. These perches have an automatic tracker that records the exact time the bird lands on the perch. One or multiple songs can be selected to be linked to each speaker, these will be selected locally from the laptop and displayed with the actual path in the program. Once the bird lands on the perch, the song or songs associated with it will be played consecutively.

**Species**: Select which species you are working with. This changes nothing about the settings or functionality of the program. The species name will appear in the final csv file. 

**Perch timeout**: Insert the time for which you want the perch to not record a new landing. For example, a timeout of 250 ms would not record a short hop on the perch by the bird. If the bird triggers a perch within less than 250ms from the previous one, the second song will not be played and the event is not recorded in the system. 

**Start time**: The time of day from which the program should be active. Before this time, landing on any of the perches does not trigger a sound playback. 

**End time**: Time of day from which the program should be inactive. After this time, landing on any of the perches triggers a sound playback, but it is not recorded in the exported datasheet.

**Save at 00:00:00**: Tick this box if the data should be automatically saved each night at midnight. This function is still under development.

**Sound A-D**: Select the files that should be played back from the matching speaker. The names of the selected files occur in the field to the right. If one file is selected, this file will be played once when the bird lands on the perch and therefore activates the microswitch. The trigger of the perch microswitch and the activation of the speaker associated is evidenced by a small click sound (user feedback).
When multiple files are selected, these will be played consecutively in the same order, from the first to the last selected (and displayed), when the bird lands on the perch and activates the microswitch. When the bird leaves and comes back to the same perch,the sequence will start from the first file to the last. There is no setting available to randomize the order of the playback files per speaker and a function that stops the previous sound if still going when the new one is activated has still to be implemented.
Clicking manually on the  Sound A button will also elicit a sound playback, mimicking the sound activated from the perch.
(***Warning***: if the audio cable is connected to the box, the sound can’t be heard while the program is not running. The speakers of the carousel are activated when the perch microswitch is activated, activating only the specific one, and at the start of the experiment when pressed the Sound A button. To hear the sound from the laptop before the start of the experiment, unplug the audio cable).

**Switching**: The program can switch the position of the perches and speakers at set time points during the day. For example, if perch 1 and Sound A are first on the right side of the carousel, this can be switched to the left side. This allows one to consider potential side preferences by the birds. The perches are from 1 to 4 (marked also in the cables and in the wooden structure) and the sounds are from A to D.

**Switching Start time**: For the first position setup, this time should correspond to the start time of the program (see above). For other position setups, this should be the time when you want that position configuration to start. 

**Switching End time**: For the last position setup, this time should correspond to the end time of the program (see above). Note that position setups cannot be overlapping in time, end times and start times should be chosen consecutively.

**Switch Position**: Indicate here which position the perches should be in. This is not a physical switching of the perches, but a switching in which sounds are played back by a landing on that particular perch. All options are available in the scroll down menu. (***Warning***: this is a key point of the program and issues can arise if no dropdown menu is selected)

**First and Last position**: Here one can indicate whether it is the first position of the day (corresponding to the start time of the program) or the last position of the day (corresponding to the end time of the program). This option doesn’t trigger anything, but it is developed to help the program and the user to track the time schedule.
Save as txt/csv: Save locally the file in the format selected (.txt; .csv)

**Clear log**: Clear the log

Press START to start the program and activate the perches.

Press END to end the program, deactivate the perches and save the file as .txt file. After the end a summary will appear in the log.

## Log screen: What is it displayed here
The log screen firstly displays all necessary detailed information about the experiment. All information similar to the following is displayed in the first line. Next, the time, date, experiment name and species name are shown. After this, information about the perches is shown: the starting position for each perch and sound, the selected perch timeout (in ms) and each sound file that is selected for each song label (A to D). Following this, the set start and end times are also shown.

Once the program has started, each time a bird lands on a perch, the log screen will display which perch the bird landed on, at which time the landing was recorded and which sound file was played back. If a bird does a small hop on the perch, faster than the perch timeout threshold, then this will be recorded as a perch timeout and not shown in the log. In case of using switching: the starting position will be displayed at the beginning of the log, all of them at the end of the experiment when pressed END. The Positions are displayed in this order: 0,1,2,3,4,5 and correspond to the section 0,2,3,4,5; not displaying the occurrences in section 6 (corresponding at the position 5) [*To correct in the next version of the softe*]. The counts are cumulative of the same song, to have the count per section, just subtract the amounts. [*To implement in the next version: count of perches*]
Furthermore, at the end of the program the log screen will show a summary of how many landings were recorded for each perch in total. 

Use the “Export as CSV” or “Export as TXT” buttons to save the log information as either “.csv” or “.txt” files, respectively. After saving the file, clear the log with the “Clear Log” button before proceeding with the next experiment. (ning: The system doesn’t need to be reactivated (closed and reopened) to work with multiple trials, anyway due large data and function handling the miss of the new settings can occur. For this reason, it is always suggested to close and reopen the softe before a new trial if possible).

Note that the log screen can be edited by clicking into it and typing. However, only use this when necessary to add additional information and do not edit any of the displayed text by the program. (***Warning***: The next information of the log screen will be placed in the next line, so be careful where the cursor is positioned!)

## End the experiment and save the trial

Press end and save the file in a location on your computer.








Figure 1: Screenshot of the user interface of the carousel program. This interface is explained in section 2 of the guideline.
