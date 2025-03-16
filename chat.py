import random
import json
import pyodbc
import torch

# SQL Server Connection
def get_db_connection():
    return pyodbc.connect('Driver={SQL Server};Server=DESKTOP-M7EQ5UN\SQLEXPRESS;Database=MedAssist;Trusted_Connection=yes;')

# Function to insert log entries
def insert_log(tag):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """INSERT INTO MedAssistUnKnownQuestions (Questions,AskedUserId,AskeDate) 
               VALUES (?,NEWID(),GetDate())"""   
    
    cursor.execute(query, (tag))
    conn.commit()
    
    cursor.close()
    conn.close()


def get_tabledata(tag):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT Description FROM MedAssit WHERE Id = ?', tag)

    row = cursor.fetchone()
    
    insert_log(tag)

    cursor.close()
    conn.close()
    
    if row:
        return row[0]
      
    else:
        return None
    

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Medica"

def get_response(msg):
  
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]
    
    insert_log(msg)
    
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:                   
                if tag == "ContactUs":            
                   result1 = get_tabledata(1) 
                   result2 = get_tabledata(2)      

                   return result1+" "+result2
                
                elif tag == "services":
                   result1 = get_tabledata(3) 
                   result2 = get_tabledata(4)
                   result3 = get_tabledata(5) 
                   result4 = get_tabledata(6)   
                   result5 = get_tabledata(7) 
                   result6 = get_tabledata(8)   
                   result7 = get_tabledata(9) 
                   result8 = get_tabledata(10)
                   result9 = get_tabledata(11)

                   return result1+" "+result2+" "+result3+" "+result4+" "+result5+" "+result6+" "+result7+" "+result8+" "+result9
                
                elif tag == "Locations":                                  
                    result1 = get_tabledata(12)                       
                    result2 = get_tabledata(13)                    
           
                    return (result1+"/t"+result2)
                
                elif tag == "AboutUs":
                    result1 = get_tabledata(14)
                    result2 = get_tabledata(15)
                    return result1+" "+result2
                
                elif tag == "WorkingTime":
                    result1 = get_tabledata(16)
                    return result1
                
                elif tag == "OurPromises":
                    result1 = get_tabledata(17)
                    return result1

                return random.choice(intent['responses'])     
     
    return "I do not understand..."




if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:     
        sentence = input("You: ") 
        if sentence == "quit":
            break      

        resp = get_response(sentence)
        print(resp)


