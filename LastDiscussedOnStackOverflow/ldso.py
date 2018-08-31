#Extracts the date of the last question posted on Stack Overflow with the given tag of a library.
#
#Requirements: 
# - You will need to change the value of user_api_key to your Stack Exchange API token
# - You will need to install PyStackExchange.
#How to run: 
# - Just run the script.

user_api_key = "your_token_here"

import stackexchange
so = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key, impose_throttling=True)
so.be_inclusive()

def main():
  with open("librarytags.txt") as f:
    tags = f.readlines()
  tags = [x.strip() for x in tags]

  for tag in tags:
    questions = so.questions(sort='creation', order='DESC', tagged=[tag,'java'])

    if len(questions) > 0:
        q = questions[0]
        print("%s - Last Discussed On Stack Overflow: %s" % (tag, q.creation_date))
    else:
        print('%s - No questions found for this tag' % tag)

if __name__ == "__main__":
  main()
