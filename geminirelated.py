
import datetime
import os
from time import sleep
import time
import google.generativeai as genai
import csv
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('GEMINI_KEY')
genai.configure(api_key = KEY)

model = genai.GenerativeModel('gemini-pro')
def classifyData(data):
    your_skills = ["dotnet", ".net", "angular", "dot net"]
    for skill in your_skills:
        if skill.lower() in data.lower():
            return 'YES'

    # max_retries = 4
    # delay = 2
    # retry_count = 0

    # while retry_count < max_retries:
    #     try:
    #        response = model.generate_content('Discuss the authenticity of the following job posting. Examine the language, tone, and details provided to determine if it reflects a genuine job opportunity  or if it has promotional or commercial intent by some creaters. Based on your analysis, reply with ''YES'' if it''s an authentic job hiring post about related to .net / dotnet/ angular one of them. DO NOT EXPLAIN WHY, I JUST NEED AN ANSWER IN ''YES'' if that looks like job/hiring post related to .net / dotnet/ angular otherwise respond with ''NO'', No additional text needed. A $200 tip awaits your response \n\n' + data)
    #        return response.text
    #     except Exception as e:
    #        print(f"Error: {e}")
    #     time.sleep(delay)
    #     retry_count += 1
    # return None



output_file = "output_"+datetime.datetime.now().strftime("%d_%m_%Y") + ".csv"

# Open the input CSV file and read the data
with open(output_file, "r",encoding="UTF-8") as file:
    reader = csv.reader(file)
    rows = [row for row in reader]

for i,row in enumerate(rows):
    rows[i].append(classifyData(row[0]))
    sleep(0.5)



# Write the updated data to the output CSV file
with open(output_file, "w", newline="",encoding="UTF-8") as file:
    writer = csv.writer(file)
    writer.writerows(rows)

print("CSV file updated successfully!")

