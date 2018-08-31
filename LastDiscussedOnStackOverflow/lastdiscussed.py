#Extracts the date of the last question posted on Stackoverflow that contains the tag of a specific library.
#Uses the file librarytags.txt
#How to use: just run it without any command line arguments.

user_api_key = "yourkeyhere"

import stackexchange
so = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key, impose_throttling=True)
so.be_inclusive()

def main():
  with open("librarytags.txt") as f:
    tags = f.readlines()
  tags = [x.strip() for x in tags]

  for tag in tags:
    print(tag + ": ")
    questions = so.recent_questions(pagesize=10, filter='_b', tagged=[tag,'java'])

    if len(questions) > 0:
        q = questions[0]
        print(q.creation_date)
    else:
        print('No questions found')
    print("")

if __name__ == "__main__":
  main()
