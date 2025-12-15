import google.generativeai as genai
import json
import re
import argparse
import math


class text_comparison_creator:

    def __init__(self, f_en, f_lang, Api_key):
        self.file1 = f_lang
        self.file2 = f_en
        self.list_of_hits=[]
        self.lines_in_f1=0
        self.lines_in_f2=0
        self.instances=10


        with open(self.file2, 'r',encoding="utf-8") as f:
            lines = f.readlines()
            self.lines_in_f2=len(lines)
        with open(self.file1, 'r',encoding="utf-8") as f:
            lines = f.readlines()
            self.lines_in_f1=len(lines)
        
        genai.configure(api_key=Api_key)
        # for m in genai.list_models():
        #     if 'generateContent' in m.supported_generation_methods:
        #         # print(m.name)
        # exit
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")
        
    # match up the anchors in both texts so can pattern match later to extract those.

    def get_anchors_llm(self):
        response_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "anchors_eng_plus_other_lan": {"type": "string"},  # JSON string
    },
    "required": ["title", "anchors_eng_plus_other_lan"]
}
        lines=[]
        with open(self.file2, 'r',encoding="utf-8") as f:
            lines = f.readlines()
            self.lines_in_f2=len(lines)
        lines=lines[:500]
        anchor_test_en=lines
        anchor_text_en=" ".join(anchor_test_en)
        with open(self.file1, 'r',encoding="utf-8") as f:
            lines = f.readlines()
            self.lines_in_f1=len(lines)
        anchor_test_lang=lines[:500]
        anchor_text_lang=" ".join(anchor_test_lang)

        # this is really really really frusterating to get a good prompt.... :(
        c1="Other-language text:\n:"+anchor_text_lang+"\n\n English translation text:\n"+anchor_text_en+"\n\n"
        c2="Task:\n" + \
             " Identify ALL of the anchors in the other-language text that correspond to structural division and find their corresponding anchors in the English translation. " + \
             "If no match is found for one of the languages, use 'XXXX' as the value."
        c3 = "Output format:\n" + \
                "Return a JSON list of objects, where each object has two keys:\n" + \
                "- 'other_lang': the anchor from the other-language text\n" + \
                "- 'eng': the corresponding anchor in English\n" + \
                "Example:\n" + \
                    "[{'other_lang': 'anchor in other language', 'eng': 'corresponding English anchor'},\n" + \
                    " {'other_lang': 'another anchor', 'eng': 'XXXX'}]\n"
        c4 = "Important:\n"+\
            "- Do NOT translate the other-language anchors. INSTEAD USE THEM EXACTLY AS THEY APPEAR. **DO NOT ADD : BEFORE THEM**\n"+\
            "- Use the English anchor exactly as it appears if it exists.\n"+\
            "- If the English anchor is missing or unclear, use 'XXXX'.\n"+\
            "- If the corresponding English text contains a chapter, volume, or section number (e.g., 'CHAPTER 1:', 'VOLUME II', 'SECTION B'), **YOU MUST USE THIS LABELING STRUCTURE** as the value for 'eng'. The descriptive title following the number must be excluded.\\n"+\
            "- Output only the JSON list; do not add extra text."+\
            "- If only **ONE anchor is found** for the origional text, generate the rest of them if there is an apparent pattern"

        
        content=c1+c2+c3+c4
        response = self.model.generate_content(contents=content,generation_config={"response_mime_type": "application/json"})
        return response


    def grep_anchors(self, text_name, wordlist):
        # print("running on text")
        lines=[]
        new_wordlist=[]
        copy_wordlist=wordlist.copy()
        with open(text_name, 'r', encoding="utf-8") as f:
            lines=f.readlines()
        copy_index=0
        for i, line, in enumerate(lines):
            # print(line)
            # print(copy_wordlist[copy_index])
            # makes assumption is is alone on line at start
            for i2, x in enumerate(copy_wordlist[:]):
                if x in line and "<a href=" not in line:
                # get rid of html stuffs
                    t=re.sub(r"<[^>]+>", "", line).strip()
                    context=""
                    for p in lines[i:i+4]:
                        cleaned=re.sub(r"<[^>]+>", "", p).strip()
                        cleaned=re.sub(r"\n","",cleaned)
                        context=context+cleaned
                    try:
                        context=context[:200]
                    except Exception as e:
                        pass
                    # print(context)
                    # print(type(context))
                    # print(t)
                    # print(copy_wordlist[copy_index])
                    if(t.startswith(x)):
                        if new_wordlist:
                            end_context=""
                            for p in lines[max(i-20, new_wordlist[-1][0]):i-1]:
                                cleaned=re.sub(r"<[^>]+>", "", p).strip()
                                cleaned=re.sub(r"\n","",cleaned)
                                end_context=end_context+cleaned
                            temp=list(new_wordlist[-1])
                            temp.append(end_context)
                            replace_touple=tuple(temp)
                            # new_wordlist[-1]=replace_touple
                        new_wordlist.append((i,line.strip(),context))
                        copy_wordlist.pop(i2)
                        break
        return new_wordlist
    
    def round_2_llm(self,eng_locs,other_locs):
        output=""
        for x in range(min(len(eng_locs),len(other_locs))):
            output+=str(eng_locs[x])
            output+=str(other_locs[x])
            output+="\n\n"
        if(len(eng_locs)>len(other_locs)):
            for x in eng_locs[len(other_locs):]:
                output+=str(x)
                output+=(", (XXXX)\n\n")
        else:
            for x in other_locs[len(eng_locs):]:
                output+=("(XXXX)")
                output+=str(x)
        # i had gemenai format this for me
        # mostly cause wasn't sure how to make it specific enough for the llm to parse. 
        # also cause it was using the model so i could ensure the output i want. 
        txt_input=f"""
            To generate a definitive, one-to-one (LS(source language) to LT(targetted language)) alignment list between 
            sequential section headings from a Source Language (LS anchors) and the 
            formal chapters/titles from a Target Language (LT titles), ensuring the 
            LT structure remains fixed. 
            Input Data Structure 

            The input will consist of sequential blocks, each containing paired segments of information, generally structured as: 
            (IndexLT, TitleLT, TextLT, IndexLS, AnchorLS, TextLS) 
            Required Tasks and Alignment Standard 

            Define Base Structure (LT): Establish the ordered, definitive list 
            of titles (TitleLT) from the Target Language as the fixed structural 
            base for the final output. 

            Sequential LS Anchor Identification: Extract the ordered, 
            sequential list of section headings/anchors (AnchorLS) from the Source 
            Language text. 

            Strict Alignment Check: Attempt to align the current TitleLT 
            (English) with the current sequential AnchorLS (Foreign) based on: 

                Direct Title Match: Titles are identical (e.g., "GIO" -> 祇王). 
                Strong Thematic Match: The subjects or literal meanings are 
            closely synonymous, especially when resolving structural gaps (e.g., 
            "Collision of Grandees" -> 殿下乘合). 

            Anomaly Resolution (The Standard): 
                If the current AnchorLS does not clearly match the current 
            TitleLT in subject or theme, and the mismatch disrupts the sequence: 

                    Action: Drop the unmatched AnchorLS from consideration. 

                    Continue: Re-attempt the alignment check for the current TitleLT using the next sequential AnchorLS. 

                Constraint: The LT titles must not be skipped. Every LT entry 
            must be paired with an LS anchor (or the LS anchor that provides the 
            thematic fix). 

            Final Output Format 

            Produce a single JSON list of objects, representing the fixed LT 
            sequence(labeled as eng) and the corresponding LS anchors(labeled as other_lang) , prioritizing the re-indexed 
            sequence established by the dropping mechanism.

            **INPUT:**
            {output}

        """
        # total=txt_input+c3
        print(txt_input)
        response=""
        response = self.model.generate_content(contents=txt_input,generation_config={"response_mime_type": "application/json"})
        return response

    # caps at 5 per to find out context
    def grep_lines_surrounding_word_in_translated_text(self, wordlist, context=2,anchor_list=[]):
        lines=[]
        # print(wordlist)
        with open(self.file2, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        list_of_hits=[]
        list_of_hits_context=[]
        copy_word_list=wordlist.copy()
        total_number_per_word=self.instances
        word_usage=[int(total_number_per_word)]*len(copy_word_list)
        for i, line in enumerate(lines):
            for i2,x in enumerate(copy_word_list[:]):
                # print(x,line)
                if x.strip() in line:
                    # bounds checks on slicing
                    start = max(0, i - context)
                    end = min(len(lines), i + context + 1)
                    # convert list to string and add it to the list of hits.
                    list_of_hits_context.append(x)
                    part1="".join(lines[start:end])
                    # print(word_usage)
                    if(word_usage[i2]>0):
                        list_of_hits.append((x.strip(),i,part1))
                        word_usage[i2]-=1
        return list_of_hits
    


    def get_information_context_untranslated_text(self,feed_list):
        l1=[]
        l2=[]
        # so word, possible window location, context for quote in english, rel loc in chapter,
        # so word, (rel location_of_other_chapter stuff, upper part of that, low part of that), context for quote in english ,rel_loc_of_chapter
        # feed_list.append((x[0],(rel_loc_of_chapter_other, upper_quote_un,lower_quote_un),x[2],rel_loc_of_chapter))


        # wnat to keep word, window loation context, context for quote in english
        # want to generate literal translation for the line, word in source language, what it means, who it refers to, 



        with open(self.file1, 'r', encoding="utf-8") as f:
            l2 = f.readlines()

        formatted_feed=[]
        for x in feed_list:
            # print(x[1][2])
            # print(x[1][1])
            context_line=l2[x[1][2]-1:x[1][1]]
            # print(context_line)
            joined_line=' '.join(context_line)
            cleaned=re.sub(r"<[^>]+>", "", joined_line).strip()
            cleaned=re.sub(r"\n","",cleaned)
            formatted_x2=re.sub(r"<[^>]+>", "", x[2]).strip()
            formatted_x2=re.sub(r"\n","",formatted_x2)
            formatted_feed.append((x[0],cleaned, formatted_x2,x[3]))
        print(formatted_feed)


        output="""
         Given a list of tuples containing the format:

        (english word, other language sentence context, English context, line number)

        You need to:
        Match Context: Identify the section in the other language text that most closely corresponds to the English context.

        Identify Word: Within that identified section, find the single other language word that best matches the meaning of the given English word.

        Produce Output: Produce a single JSON object for each tuple, adhering strictly to the following structure and content requirements:{"other_lang":word in source language also with how to pronounce it, "word_eng":the word in english,"part_of_speech":part of speech, context_summerary:**3 sentance max** summary of context for the word's use. } 
        """
        str_formatted_feed=""
        for x in formatted_feed:
            str_formatted_feed=str(x)
            output+=f"input:/n{str_formatted_feed}"
        # print(output)
        # response=None
        # more_advanced_model = genai.GenerativeModel("models/gemini-2.5-flash")
        response=self.model.generate_content(contents=output,generation_config={"response_mime_type": "application/json"})
        return response


if __name__ == "__main__":


    parser = argparse.ArgumentParser(
                    prog='first part in the pipeline series',
                    description='gets the prospective anchors and stores their matches',
                    epilog='Text at the bottom of help')
    parser.add_argument('TRANSLATED_FILEPATH')   
    parser.add_argument('ORIGIONAL_FILEPATH')    
    parser.add_argument('ANCHOR_FILE')
    parser.add_argument('WORD_LIST')
    parser.add_argument('-o', '--output_file')     
    parser.add_argument('-s' '--sp_output_file')
    parser.add_argument('-i' '--instances_per_word')
    

    args = parser.parse_args()

    word_list=[]
    data=[]

    with open(args.ANCHOR_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open("Key.file","r",encoding="utf-8") as f:
        key=f.readline()
    
    
    with open(args.WORD_LIST,"r",encoding="utf-8") as f:
        word_list=f.readlines()
    for x in range(len(word_list)):
        word_list[x]=word_list[x].strip()
    word_list=[word for word in  word_list if word!='']
    # print(len(word_list))
    # print(word_list)
    t1=text_comparison_creator(args.TRANSLATED_FILEPATH, args.ORIGIONAL_FILEPATH,key)

    if(args.i__instances_per_word):
        t1.instances=args.i__instances_per_word

    with open(args.ORIGIONAL_FILEPATH,'r',encoding="utf-8") as f:
        word_list2=f.readlines()
        # print(len(word_list2))

    # clean up the anchors
    # it's been like a couple nights idk why volume isn't
    temp_dropping = [entry for entry in data
            # needs to exist so drop if see XXXX
            # may not need to grab entry['eng] for volume??? thing maybe???
            if entry['eng'] != 'XXXX' and entry['other_lang'] != 'XXXX' and ('VOLUME' not in  entry['eng'])
    ]


    # print(temp_dropping)
    grab_str=""
    # get rid of the thingy? thingy being the volime entry here
    # print(temp_dropping)
    if temp_dropping:
        guess=temp_dropping[0]['eng'].strip().split(" ")[0]
    # print(guess)
    english_list = [pos['eng'] for pos in temp_dropping]
    
    if all(guess in pos for pos in english_list):
        grab_str=guess
        # print("HERE")
        for i,entry in enumerate(data):
            if(entry['eng']=="XXXX"):
                data[i]['eng']=grab_str
    # print(args)
    # put back on final pass
    second_pass=args.s__sp_output_file

    if(not second_pass):
    # print(data)
    # cut out rest of XXXXX if not common thread between stuff
        data = [entry for entry in data
                # needs to exist so drop if see XXXX
                if entry['eng'] != 'XXXX' and entry['other_lang'] != 'XXXX'
        ]
    
    english_list = [entry['eng'] for entry in data]
    greek_list = [entry['other_lang'] for entry in data]
    

        # print(english_list,greek_list)
    # for i in range(len(english_list)):
    #     print(english_list[i], greek_list[i])

    eng_locs=t1.grep_anchors(t1.file2,english_list)
    other_locs=t1.grep_anchors(t1.file1,greek_list)
    # print(other_locs)
    # print("other lanugage anchors")
    # print(other_locs)
    # print("english anchors")
    # print(eng_locs)

    if(second_pass):
        resp=t1.round_2_llm(eng_locs,other_locs)
        data=resp._result
        # get the response text from the llm
        str1=data.candidates[0].content.parts[0].text
        print(type(str1))
        print(str1)
        with open(second_pass,'w',encoding="utf-8") as f:
            f.write(str1)
        exit
    

    # for x in range(min(len(eng_locs),len(other_locs))):
    #     print(eng_locs[x],other_locs[x])

    # if(len(eng_locs)>len(other_locs)):
    #     for x in eng_locs[len(other_locs):]:
    #         print(x,"XXXX")
    # else:
    #     for x in other_locs[len(eng_locs):]:
    #         print("XXXX",x)


    if(len(eng_locs)==0 or len(other_locs)==0):
        exit
    # print("HERE")
    # if in header get rid of them
    # print(eng_locs)
    # print(other_locs)
    locs_of_surrounding_words=t1.grep_lines_surrounding_word_in_translated_text(word_list)
    # print(locs_of_surrounding_words)
    # print(locs_of_surrounding_words)

    # get the current chapter anchor to then feed to it. 
    # list of locs_to_extract in the source text
    feed_list=[]
    for x in locs_of_surrounding_words:
        for num, y in enumerate(eng_locs):
            top_of_chapter=eng_locs[min(len(eng_locs)-1,num+1)][0]
            bottom_of_chapter=y[0]
            if(top_of_chapter==bottom_of_chapter):
                top_of_chapter=t1.lines_in_f2
            if x[1]>bottom_of_chapter and top_of_chapter>x[1]:
                # print(x[1],y[0],x[1]-y[0])
                rel_loc_of_chapter=(x[1]-y[0])/(top_of_chapter-bottom_of_chapter)
                start_of_current_anchor=other_locs[min(len(other_locs)-1,num)][0]
                # print(start_of_current_anchor)
                # top_of_chapter=eng_locs[min(len(eng_locs)-1,num+1)][0]
                # print(top_of_chapter)
                start_of_next_anchor=other_locs[min(len(other_locs)-1,num+1)][0]
                # print(start_of_next_anchor)
                # print(rel_loc_of_chapter)
                if start_of_current_anchor==start_of_next_anchor:
                    # get rest of file in terms of length of lines to extract
                    start_of_next_anchor=t1.lines_in_f1
                    # print(t1.lines_in_f1)
                rel_loc_of_chapter_other=(int)((rel_loc_of_chapter)*(start_of_next_anchor-start_of_current_anchor))+start_of_current_anchor
                # print(rel_loc_of_chapter_other)
                len_of_rel_chapter_other=start_of_next_anchor-start_of_current_anchor
                # grab a part of the chapter to ensure that you are grabbinh enough of it
                percent10_of_chapter=min(math.ceil((len_of_rel_chapter_other*0.25)),75)
                upper_quote_un= min(rel_loc_of_chapter_other+percent10_of_chapter,start_of_next_anchor)

                lower_quote_un=max(rel_loc_of_chapter_other-percent10_of_chapter,start_of_current_anchor)
                # 
                feed_list.append((x[0],(rel_loc_of_chapter_other, upper_quote_un,lower_quote_un),x[2],x[1]))
                break
    # print(feed_list)
    resp=t1.get_information_context_untranslated_text(feed_list)
    data=resp._result
    # get the response text from the llm
    str1=data.candidates[0].content.parts[0].text
    if(args.output_file):
        print(type(str1))
        print(str1)
        with open(args.output_file,'w',encoding="utf-8") as f:
            f.write(str1)
    else:
        with open("default_output.txt",'w',encoding="utf-8") as f:
            f.write(str1)

    # json_text_block = response.result.candidates[0].content.parts[0].text
    # # The text includes triple backticks and "json", strip them
    # json_text = json_text_block.strip("` \njson")
    # print(json_text)



