import google.generativeai as palm
import requests
import sys
import re
import time
import json

if len(sys.argv) < 4:
    print("Usage: python palm_error_handled.py <Instance> <Count_Per_Instance> <API_Key>")
    sys.exit(1)

Instance = sys.argv[1]
Count_Per_Instance = sys.argv[2]
API_Key = sys.argv[3]

Start_index = int(Instance)*int(Count_Per_Instance)
End_index = Start_index+int(Count_Per_Instance)
print(Start_index,End_index)

defaults = {
    'model': 'models/chat-bison-001',
    'temperature': 0.25,
    'candidate_count': 1,
    'top_k': 20,
    'top_p': 0.95,
}
Result_Filename = "descriptions_Palm.txt"
f = open(Result_Filename, "w")

def string_to_dict(input_string):
    try:
        dictionary = json.loads(input_string)
        return dictionary
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None
        
def remove_html_tags_and_urls(text):
    clean_text = re.sub(r'<[^>]*>', ' ', text)
    clean_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', clean_text)
    clean_text = re.sub(r'[^a-zA-Z0-9\s,.]', ' ', clean_text)
    clean_text = re.sub(r'\,\s+', ',', clean_text)
    clean_text = re.sub(r',{2,}', ',', clean_text)
    # clean_text = re.sub(r'[^\w\s,.]', ' ', clean_text)
    # clean_text = remove_non_english_words(clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text.strip()

with open("prompts.txt", encoding='utf-8', errors='ignore') as f:
    check_index = 0
    for line in f:
        website, firm = line.strip().split('\t')
        
        if Start_index <= check_index <= End_index:
            
            # url_list = url_list[Start_index:End_index]
            print("website: ", website)
            # firm = string_to_dict(firm)
            # firm = firm.get('description')
            # exit
            Search_Firm = firm[0:3000]
            # print("firm: ", firm[0:3000])
           

            palm.configure(api_key=API_Key)
            
            retries = 3
            for attempt in range(retries):
                try:
                    response = palm.chat(messages='Summarize the business in 30 words, focusing only on products, services and solutions based on below meta data. Exclude input prompt, address, copyright info, history and service commitment.' + Search_Firm +'', **defaults)
                    
                    print(type(response))

                    if response.candidates[0]['content']:
                        description = response.candidates[0]['content']
                        print(description)
                        break  # Break out of the retry loop if successful
                    else:
                        print(f"Attempt {attempt+1} failed. Retrying...")
                        time.sleep(1)  # Wait for 1 second before retrying

                except Exception as e:
                    print(f"Error: {str(e)}")
                    print(f"Attempt {attempt+1} failed. Retrying...")
                    time.sleep(1)  # Wait for 1 second before retrying

            # Check if all retries failed
            if not response.messages[0]['content']:
                print(f"Error after {retries} attempts. Status: {response.status}")
                continue  # Move to the next iteration if there's an error

            if not isinstance(description, str):
                description = str(description)

            # Clean up the description
            
            # description = re.sub(r"\n", "", description)
            # print(description)
            
            description = re.sub(r'.*[\"\']content[\"\']\:\s*[\"\']',"", description)
           
            # description = re.sub(r'\s*[\"\']\}\]\,\s*filters\=\[\]\,\s*top\_p\=0\.\s*\d+\,\s*top\_k\=\d+\)',"", description)
            description = re.sub(r'\. The company also offers.*\.',"", description)
            description = re.sub(r'The company offers a wide range of ',"The company offers ", description)
            description = re.sub(r'The company offers a variety of ',"The company offers ", description)
                # description = re.sub(r'.* is a website', f'{firm} is a company', description)
                # description = re.sub(r'www.*com is a', f'{firm} is a', description)
                # description = re.sub(r"www\.*com", firm, description)
                # description = re.sub(r"\b(?:\w+\.)*(?:com|net|org|tv|edu|us|ca|co)(?=/|\s|$)", firm, description)
                # description = re.sub(r"\s.*\.(?:com|net|org|tv|edu|us|ca|co)(?=/|\s|$)", firm, description)
            description = re.sub(r'is a company that', '', description)
            description = re.sub(r'Here\s*is\s*a\s*\d+\-word\s*summary\s*of\s*the\s*business\:', '', description)
            description = re.sub(r"They also offer", "The company also offers", description)
            description = re.sub(r"we offer", "the company offers", description)
            description = re.sub(r"We offer", "The company offers", description)
            description = re.sub(r"We are", "The Company is", description)
            description = re.sub(r"They offer", "The company offers", description)
            description = re.sub(r"The site offers", "The company offers", description)
            description = re.sub(r"The website offers", "The company also offers", description)
            description = re.sub(r"The website also offers", "The company also offers", description)
            description = re.sub(r"The website also", "The company also", description)
            description = re.sub(r"The website provides", "The company provides", description)
            description = re.sub(r"The website includes", "The company includes", description)
            description = re.sub(r"The website also provides", "The company also provides", description)
            description = re.sub(r"The website also includes", "The company also includes", description)
            description = re.sub(r"The site also offers", "The company also offers", description)
            description = re.sub(r"The site also provides", "The company also provides", description)
            description = re.sub(r"The site also includes", "The company also includes", description)
            description = re.sub(r"The site offers", "The company offers", description)
            description = re.sub(r"The site provides", "The company provides", description)
            description = re.sub(r"The site includes", "The company includes", description)
            description = re.sub(r"Their product", "The company product", description)
            description = re.sub(r"Their website offers", "The company offer", description)
            description = re.sub(r"Their website provides", "The company provides", description)
            description = re.sub(r"Their website includes", "The company includes", description)
            description = re.sub(r"They also", "The company also", description)
            description = re.sub(r"The website", "The company", description)
            description = re.sub(r"We also offer", "The company also offers", description)
            description = re.sub(r"a variety of services such as ", "", description)
            description = re.sub(r"a variety of products such as ", "", description)
            description = re.sub(r"a variety of products and services such as ", "", description)
            description = re.sub(r"The site", "The company", description)
            description = re.sub(r" Llc", " LLC", description)
            description = re.sub(r" Lp ", " LP ", description)
            description = re.sub(r"Our products", "Products", description)
            description = re.sub(r"Their", "Our", description)
            description = re.sub(r"/", "", description)
            description = re.sub(r"\\n", "", description)
            description = re.sub(r"\\s", "", description)
            description = re.sub(r"\\r", "", description)
            description = re.sub(r"\*", "", description)
            description = re.sub(r"\.(?!\s)", ". ", description)
            description = re.sub(r'\s+', ' ', description)
            description = remove_html_tags_and_urls(description)
            description = re.sub(r' \s*\'\}]\,\s*filters\=\[\]\,\s*top_p\=\d+\.\s*\d+\,\s*top_k\=\d+\,\s*_client\=',"", description)
            # description = re.sub(r'[^a-zA-Z0-9\s]', ' ', description)
            description = description.strip()
            # ... (your existing cleanup code)
            print("Afetr changing")
            print(description)

            # Check if the description is empty
            if not description:
                print("No description generated for website: ", website)
                continue

            # Write the description to a text file
            
            with open(Result_Filename, "a", encoding='utf-8') as f:
                f.write(website + "\t" + description + "\n")
        check_index+=1