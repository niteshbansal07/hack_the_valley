from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
import cohere
import csv
from cohere.classify import Example


app = Flask(__name__)

bootstrap = Bootstrap5(app)
#api key and activating the key
api_key = 'k10bD3dfeC3VW7neuosKNR6yQlyItQLfLlScsIVQ'
co = cohere.Client(api_key)
issue = r'./static/issues_and_situations.csv'
perspective = r'./static/Internal_external.csv'
vague = r'./static/vague.csv'
stress_keyword = r'./static/stress_keyword.csv'

def read_csv(csv_name):
    with open(csv_name, encoding="utf8") as f:
        csv_reader = csv.reader(f)
        statement = []
        result = []
        for line in csv_reader:
            statement.append(line[0])
            result.append(line[1])
        return (statement, result)


def predic_confid(returnstr):
    def parse_data(str_to_parse: str, keyword: str):
        LEEWAY = 15
        keyword_indice = str_to_parse.find(keyword) + len(keyword)
        str_to_parse = str_to_parse[keyword_indice:keyword_indice + LEEWAY]
        str_to_parse = str_to_parse[str_to_parse.find('\n')-1::-1]
        # reversing the resultant as we read the string backwards
        resultant = str_to_parse[::-1]
        return resultant


    #isolating the prediction

    prediction = parse_data(returnstr, 'prediction: ')
    #searching for the prediction and its matching confidence level
    str_to_find = (prediction+'\n\tconfidence: 0')
    confidence = parse_data(returnstr, str_to_find)

    return (prediction, confidence)


def generate_examples(csv_name:str, statement_indice: int, result_indice: int):
    training_data = read_csv(csv_name)
    example_list = []
    for i in range (len(training_data[statement_indice])):
        example_list.append(Example(training_data[statement_indice][i],
                                    training_data[result_indice][i]))
    return example_list


#try to classify what issue the user is dealing with
def senti_analysis(str_to_analyse: str, file_name: str):
    examples = generate_examples(file_name, 0, 1)

    inputs = [str_to_analyse]
    response = co.classify(
      model='small',
      inputs=inputs,
      examples=examples)

    return(response.classifications)

#first message
def keyword_extract(stress_statement: str):
    string_formatted = '\n--\nStatement: '+stress_statement+'\nEvent:'
    response = co.generate(
      model='small',
      prompt='Statement: School is stressing me out\nEvent: School\n--\nStatement: My wife is divorcing me\nEvent: divorcing\n--\nStatement: Work is overwhelming\nEvent: Work\n--\nStatement: My work is piliing up and I feel burnt out\nEvent: Work\n--\nStatement: I witnessed my classmate having a breakdown in school\nEvent: school\n--\nStatement: My project deadline is coming up and I\'m nowhere near done\nEvent: project\n--\nStatement: I\'m stressed\nEvent: none\n--\nStatement: I got fired from my job and now I\'m worried about money\nEvent: money\n--\nStatement: I\'m feeling under the weather\nEvent: none\n--\nStatement: I feel like I have no control over my life\nEvent: none\n--\nStatement: I had the biggest mental breakdown of the day today. If I go to high school, I come home tired, loads of homework, and big eye bags. And if I miss a day I’m still tired, have loads of homework and with even bigger eye bags\nEvent: school\n--\nStatement: I am stressing out and feel like the one person I want to talk to about it with, I can’t.\nEvent: none\n--\nStatement: I am worried about starting in my new work position\nEvent: work\n--\nStatement: I\'m meeting with a work recruiter, I feel anxious and unprepared to talk with them\nEvent: work\n--\nStatement: My boyfriend is constantly stresssed about everything\nEvent: none\n--\nStatement: I\'m stressed about doing my first presentation in front of a large crowd\nEvent: presentation\n--\nStatement: I want make my family proud, I feel like I\'m letting them down and I\'m always thinking about how tiring it all is\nEvent: family\n--\nStatement: Recently I started really stressing out emotionally, compartmentalizing my stress and pushing it deep down\nEvent: none\n--\nStatement: My sister has been anxious lately, at night, even though she is exhausted, she can\'t sleep because her mind racies. She started getting sick and missing school.\nEvent: none\n--\nStatement: During these last few months of my senior year, I\'ve been more stressed than ever before. I find the idea of choosing a school to spend the next four years unbearably daunting\nEvent: school\n--\nStatement: One of the biggest stressors in my life right now is relationships\nEvent: relationships\n--\nStatement: I haven\'t been able to find an internship for the summer yet, and I\'m worried I might not be able to do so in time.\nEvent: internship\n--\nStatement: When I\'m stressed, it\'s either because of social things, like feeling like I don\'t fit in\nEvent: social\n--\nStatement: I feel so behind in school, everyone is developing cool projects for their final projects and here I am making a basic html webpage\nEvent: school\n--\nStatement: I don\'t know if I want to continue studying psychology, I\'m stressing about the future\nEvent: future\n--\nStatement: My work makes my life a living hell, stress and constant pressure\nEvent: work\n--\nStatement: I work as a nurse in a failling hospital and I take pride in my work, but it is overwhelming everyone at work including me\nEvent: work\n--\nStatement: I can\'t help anyone, everytime I try stress overwhelms me\nEvent: none\n--\nStatement: I feel unprepared for exams, I don\'t want to fail\nEvent: exams\n--\nStatement: My coworkers keep swearing at me and insulting me, it makes me anxious\nEvent: work\n--\nStatement: I\'m so stressed because of this hackathon\nEvent: hackathon\n--\nStatement: My relationship is stressing me out\nEvent: relationship'+string_formatted,
      max_tokens=10,
      temperature=0.3,
      k=0,
      p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stop_sequences=["--"],
      return_likelihoods='NONE')
    return str('{}'.format(response.generations[-1].text))

#firstmessage
def check_vague(message: str):
    #checking how vague a message is with sentiment
    vague_data = str(senti_analysis(message, vague))
    return predic_confid(vague_data)


def summary(messages: list):
    string_message = ''
    for i in messages:
        string_message+=i
    string_message = '\nPassage: '+ string_message +'\n\nTLDR:'
    response = co.generate(
      model='large',
      prompt='Passage: I am so stressed. My family is on my case about my best friend\'s behavior and it’s affecting me physically and emotionally. I just had a horrible panic/anxiety attack since I\'m staying awake later and drinking more coffee and energy drinks. My digestive system is all messed up and I have the worst body pains. I take a lot on. And I let things bother me so much. I can\'t talk to my family, I can\'t talk to my friends, I feel like I can\'t talk to anyone. I\'ve tried to cope by ignoring them, but it hasn\'t worked, they bring up my friend everytime I see them. Whenever I get too stressed out about it I go out for a walk and listen to music to avoid thinking about it. I don\'t regret being friends with my best friend, but I do regret bringing them around my parents.\n\nTLDR: My friend and my family are stressing me out and affecting my mental and physical health. I feel stuck, not able to talk with either my friends or my family. It makes me more tired, so I\'m depending on caffeine to stay awake. It messes up my digestive system. I try to cope by listening to music and getting away by taking a walk.    \n--\nPassage: I feel like I get stressed out by work much more than the average person. It\'s not like I have to stretch a lot at work (10-11 hours max a day) but I still feel incredibly overwhelmed. Whenever there is a problem at work, I feel like I cannot rest until I have it resolved. I have to work on a lot of short term projects with tight deadlines and on top of that I get ad-hocs from stakeholders. I don\'t really have any BAU work, or work that I can do without having to think much. Almost every project comes with it\'s own unique set of problems that I have never encountered before and I get about 2-3 projects like this every week where I have to figure out something from scratch. Also since these tasks come from stakeholders and not my boss, the stakeholders also put pressure on us to resolve things quickly.I feel like my primary cause of stress is that I can never predict what kind of work and what new problems will be thrown at me this week. How many stakeholders\' expectations I\'d have to manage, how much problem solving I\'d have to do. I get really tense and cry a lot.  \n\nTLDR: Work makes me very stressed, I feel overwhelmed and I feel obligated to to resolve any and all problems I encounter. I work on short deadlines and every project has unique, erratic and stressful requirements.\n--\nPassage: I’ve just started my first job out of uni in a very high stress field with strict timelines. I’ve noticed that when I send out emails, I overthink and stress over every little bit (aka am I spelling names correctly, does it make sense) to the point I’m wasting time. When I do send out ‘wrong’ emails (aka it double sent or some wires were crossed) I freak out and get way too much adrenaline - I feel like I’ll puke and I get very warm. I know I won’t lose my job over this but I can’t help but overthink. It’s literally to the point that I’m wondering whether this is the right field for me even though I really do like my job. I feel too embarrassed to talk with my boss or coworkers about it. I usually try to dismiss my worries as me overreacting, but everytime I do I just think about just how badly I can mess up.\n\nTLDR: My first job has strict deadlines, so if I\'m too meticulous with my emails I feel like I\'m wasting time. It\'s to the point If I\'m not certain my email is perfect I worry or I send an email with a mistake I freak out.\n--\nPassage: We had a chemistry quiz today. It isn’t that important since it won’t affect our grades in any way but I still feel bad about it. The quiz went kinda bad. When I talked with my classmates they told me that it was hard as well but I’m still stressed out about it because I know that some of the best students will get good grades. I feel worthless when I’m academically not successful because from my childhood it was the only way that I felt loved and accepted by other people but as I grow up it gets harder and harder and I keep putting 0 effort because it has always been easy for me. Or it used to be. I didn’t have to put effort into being successful but now it’s not the same. I feel like a failure and I feel so worthless. I’m scared of disappointing my chemistry teacher. She literally smiled at me when the exam was over. She’s definitely going to be disappointed. I\'m actually really stressed out rn.\n\nTLDR: I\'m worried about disappointing those around me. Academics used to be easy for me, but now it\'s gotten much harder and I feel worthless. Things like today where I did badly on my chemistry quiz and disappointing my chemistry teacher.\n--\nPassage: I recently found out that my dad has stage 4 colon cancer. I have always had a very rocky relationship with him and it\'s started taking a toll on my mental state lately. I moved in with my mom since my parents are divorced, and have been since I was 4, but I am with my mom full-time now. My mom isn\'t the greatest person and is an alcoholic, and my dad isn\'t the greatest either, but they\'re both my parents and I love them to death, but I am so worried about my dad and it\'s really stressing me out.\n\nTLDR: I\'m really stressed out because recently I found out my dad has stage 4 cancer  Even though I don\'t have the best relationship with my mom or dad, I still love both of them and our rocky relationship doesn\'t change that.\n--'+string_message,
      max_tokens=30,
      temperature=0.5,
      k=0,
      p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stop_sequences=["--"],
      return_likelihoods='NONE')
    title = response.generations[-1].text
    title = title[:title.find('.')]
    title = title.strip()
    return title


def read_chat(messages: list, summarize: bool):
    # checking if the first message is vague
    first_message = str(messages[0])
    vague = check_vague(first_message)
    vague = vague[0]
    vague = vague != 'specific'
    # vague is now a True or False
    # now check whether we can isolate the cause of their stress
    cause = str(keyword_extract(first_message))
    cause = cause.replace('\n', '')
    cause = cause.replace('--', '')
    cause = cause.strip()
    if summarize:
        return summary(messages)
    return (vague, cause)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browse')
def browse():
    return render_template('browse.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/handle_data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        myfirstanswer = request.form["seeAnotherFieldGroup"]
        if myfirstanswer=="positive":
            oField1 = request.form["oField1"]
            oField2 = request.form["oField2"]
            data = oField1
        elif myfirstanswer=="negative":
            message = []
            message.append(request.form["feelings"])
            message.append(request.form["environment"])
            message.append(request.form["howEnv"])
            message.append(request.form["elaborate"])
            message.append(request.form["effects"])
            message.append(request.form["obstacles"])
            answer1 = read_chat(message, False)
            answer2 = read_chat(message, True)
        else:
            data = "Nothing"
    return render_template('index.html', data=answer2)


if __name__ == '__main__':
    app.run(debug=1)