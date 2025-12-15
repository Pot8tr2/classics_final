This runs in Python 3.11. 
Replace the contents of Key.file with your gemenai api key

This is more of a proof of concept for implementing a pipeline to grab the actual context of a word in an arbirary translated text from the source text, to understand how it was translated and what the context of that translation was. Tho, only tested it on a couple versions of the illiad and the heike, so that can definitly be improved. 
So fair note, it might be really bad outside of that, or even outside the copies I tested on.

To run the pipeline
First run anchor_extractor.py
You can verify that the file output matches the titles for the next step. 
You can fix them if necessary
Next run text_comparison_creator.py
if you want it saved you can use the -o operation.


If you want more concrete anchors you can asign them yourself in the output file for anchor_extractor
You can also fix some of the errors the llm might come up with 
It will attempt to fix them if you run the command
An example of the pipeline being run through 




What can be improved:
    A lot--efficiency of the program, probably the queries that are being asked to gemenai, also the model of it. it is on gemenai 2.5 at the min and while that does kind of work, it doesn't work in it's entirety. I was able to get all the chapters matching up to respective letter in the greek_output file without knowing that it was using greek letters. 
    Cleaning up the output can also be inproved. While it is able to get the output location and confirm that works. These anchors could also be placed at tighter spots as well, rather than just chapter locations/sections. 
    As well as packing in the searches for the program
        To avoid multiple calls in the api, it will try and pack a couple of them together. 
    Cleaning up the comments. 


    A better pipeline would be try without llm to extract anchors, if fails, then can use the llm version to get them. 

    UUUUH it probably needs context matching to cut down on usage....




