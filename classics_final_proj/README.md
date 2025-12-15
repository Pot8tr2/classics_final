This runs in Python 3.11. 
Replace the contents of Key.file with your gemenai api key

This is more of a proof of concept for implementing a pipeline to grab the actual context of a word in an arbirary translated text from the source text, to understand how it was translated and what the context of that translation was. Tho, only tested it on a couple versions of the illiad and the heike, so that can definitly be improved. 
So fair note, it might be really bad outside of that, or even outside the copies I tested on.

To run the pipeline
To generate anchors for locations in the initial context of the system, you would run:
python anchor_extractor.py english_file_location source_file location 
It also has an optional argument under -o to output these to a location
Example usage:
python anchor_extractor.py japanese_text/heike_pdf_trimmed.txt japanese_text/heike_first_chapter_jp -o anchor_list_files/heike.txt


You can verify that the file output matches the titles for the next step. 
You can fix them if necessary
if you want it saved you can use the -o operation.

To refine the anchors for the text you would run 
Python text_comparison_creator.py [translated_text] [untranslated_text] [anchor file] [word_list_file] [-s fixed_output]
Translated, untranslated, anchor, and word_list_file are all required.
-s is not required but is what your fixed output is saved to
Example:
python text_comparison_creator.py japanese_text/heike_pdf_trimmed.txt japanese_text/heike_first_chapter_jp anchor_list_files/heike.txt  wordlists/wordlis_jp.txt -s anchor_list_files/heike_fixed.txt

python text_comparison_creator.py japanese_text/heike_pdf_trimmed.txt japanese_text/heike_first_chapter_jp anchor_list_files/heike_fixed.txt  wordlists/wordlis_jp.txt -o output_files/heike_found.txt

To run this step essentially you don’t provide it with a -s flag, and instead provide it with a -o flag. 
-i also cuts off the amount of times it will find a word in the list. This is to ensure you don’t go over the token limit. If you want you can just set it to 9999 if you don’t care about that. 



What can be improved:
    A lot--efficiency of the program, probably the queries that are being asked to gemenai, also the model of it. it is on gemenai 2.5 at the min and while that does kind of work, it doesn't work in it's entirety. I was able to get all the chapters matching up to respective letter in the greek_output file without knowing that it was using greek letters. 
    Cleaning up the output can also be inproved. While it is able to get the output location and confirm that works. These anchors could also be placed at tighter spots as well, rather than just chapter locations/sections. 
    As well as packing in the searches for the program
        To avoid multiple calls in the api, it will try and pack a couple of them together. 
    Cleaning up the comments. 


    A better pipeline would be try without llm to extract anchors, if fails, then can use the llm version to get them. 

    UUUUH it probably needs context matching to cut down on usage....




