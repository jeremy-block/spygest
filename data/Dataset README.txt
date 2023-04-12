** Provenance Segment Sample
** August 21, 2019
** Eric Ragan

This zip file contains interaction logs and sample "time segments" from 24 user study sessions with participants who conducted data analysis using a visual document explorer tool. The analysis sessions were done with three different text datasets, and this sample includes data from 8 participants for each of the 3 datasets (8x3 = 24 total).

This README uses the word DATASET to refer to the source collection of text that was used for participants to analyze in the user studies. The word SAMPLE refers to the total collection of all data included in the zip file.

This sample data is organized by into three folders, one for each dataset from the user study. Each dataset folder contains three subfolders:

1) Documents
This has a single json file with all the "documents" of the dataset that the participants explored for the text analysis activity. Each "document" is really just some text (content) with associated meta data (id, title, date, type). Document content is typically a few sentences long, though some are much longer, and some may be shorter.

2) Segmentation
This has multiple csv files (one per analysis session). Each file is associated with a different participant analysis session coded by the filename prefix (e.g., "Arms_P1"). Use this prefix to match the segment file to the associated "Interaction Logs" file. Each segmentation file is a list of time periods that cover one participant's entire analysis session. Each row of the segmentation file is a period of time, where each segment has a different start time and duration (length in seconds). Each segment has a start time and end time. The start time should always start with 0 for the first segment, and each following row should have a start time that matches the end time on the previous row.

3) User Interactions
This is a collection of json files with system logs and notes from the participant analysis sessions. Each file is associated with a different participant analysis session coded by the filename prefix (e.g., "Arms_P1"). Use this prefix to match the interaction log file to the associated "Segmentation" file. Each json record is a time-ordered event with a given "InteractionType". The events correspond to different interactions possible in the document explorer tool used for the analysis. You can try a demo of the tool here: http://people.tamu.edu/~sina.mohseni/docexplorer (may need to refresh for it to work, and it is not guaranteed to still work).
> IMPORTANT: You should ignore entries with InteractionType of "Think_aloud". These are notes from a researcher or the participant rather than system logs, and therefore this data should NOT be used when generating summaries. This data can be used to help you understand the analysis records but it should be excluded from your visual analytics application.
> IMPORTANT: Times should be seconds, but the "time" in the interaction log files have been erroneously multiplied by 10. This means that you need to divide by 10 to have the time value in seconds.
> IMPORTANT: Document reading and doc_open events have a duration that show how long the mouse was over the document or how long the doc was open. The duration for all other events (like search and note-taking) is a fixed number that doesn't mean anything.
