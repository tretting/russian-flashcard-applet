# Russian Flashcard Applet
This is a simple, browser-based flashcard app meant to help with properly declining nouns and adjectives. Traditional flashcards are made one-by-one with examples that remain fixed for memorization and recall. The main feature of this flashcard deck is that it is not a deck at all---each card is randomly generated from one adjective and one noun, for which the user must come up with the correct translation based on the given gender, number, and case. In this way, the training material is meant not for rote memorization but for enhancing pattern recognition and recall in a dynamic way closer to the real world. Please be aware that some adjective-noun pairings will appear unnatural (for example. 'healthy north' or 'habitual Germany')---this is a feature of the randomly-generated cards that I do not have a safeguard against. This is my first foray into the domain of interactive html-based applications, so feedback is highly appreciated. This is very much a side project and I may not hear or see your feedback for some time, I am sharing it here for any Russian learners who, similarly to me, found other resources in this area lacking. That said, below are the steps required to get everything running for your machine. 

Note: the database file which the applet runs from is about 180MB, which is too large for upload. This is because it contains all of the data from the openrussian.org online database. So, I include the steps to build it yourself.

#### Step 1:
Create a directory on your local machine to hold all files and folders. I use VScode as it makes setup of everything quite straightforward. In the top level of my directory, I have all .py codes. Ensure the .css file is in the static folder, the .js files are in the templates folder, and the venv folder holds the other utilities for the code (in my case, VScode handles this portion). I will not cover here how to install python and the necessary packages onto your machine.

#### Step 2:
Navigate to <https://en.openrussian.org/dictionary> and click on the 'TogetherDB Online Database' hyperlink. You will need to download the following tables as .csv files:

- nouns
- adjectives
- verbs
- sentences
- translations
- words
- words_forms

To download the table which you have open, click on the triple-dot icon on its tab and select export table. Be sure to save it as a .csv file with comma delimiters. Ensure that they are stored in the top level of your directory and that the naming conventions used when saving them match the naming convention you use in the db_prep.py file. For example, the code reads the 'nouns' table .csv file as 'ru_nou.csv'. Finally, run the db_prep.py file and ensure that the .db database file has now appeared in the top level of your directory.

#### Step 3:
Open your terminal/command prompt and navigate to the top level of your directory which contains the flashcard_applet.py python script. Then enter the command 'python flashcard_applet.py'. The console will display the address running your app. Navigate in your browser to this address and click on the 'Case Practice' button. You can choose between different levels of vocabulary depth at the top of the page. Above the flashcard are what/who question words associated with the required translation case, along with the requirement to translate into either masculine (m), feminine (f), neuter (n), or plural (pl). To flip the card between the Russian and English translations, press the spacebar. The flashcard can be advanced by either clicking 'Next Exercise' or by simply pressing the right-arrow key.

Happy learning!


