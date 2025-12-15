# this file is essentially to get the first part of the response for llm 
# this allows me not to use more api calls on it. 
# it will save it under file 
# can edit that file later if need be


import text_comparison_creator
import json
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='first part in the pipeline series',
                    description='gets the prospective anchors and stores their matches',
                    epilog='Text at the bottom of help')
    parser.add_argument('TRANSLATED_FILEPATH')   
    parser.add_argument('ORIGIONAL_FILEPATH')    
    parser.add_argument('-o', '--output_file')      
    

    args = parser.parse_args()
    print(args)

    output_file=args.output_file
    translated_filepath=args.TRANSLATED_FILEPATH
    origional_lang_file=args.ORIGIONAL_FILEPATH
    key=""
    with open("Key.file", 'r') as f:
        key=f.readline()
    print(key)

    t1=text_comparison_creator.text_comparison_creator(translated_filepath, origional_lang_file,key)
    response=t1.get_anchors_llm()

    print(response._result)
    data=response._result
    # get the response text from the llm
    str1=data.candidates[0].content.parts[0].text
    print(type(str1))
    print(str1)
    with open(output_file,'w',encoding="utf-8") as f:
        f.write(str1)



