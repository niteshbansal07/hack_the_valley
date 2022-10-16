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
positive_story = r'./static/stress_positive.csv'


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
      model='medium',
      inputs=inputs,
      examples=examples)

    return(response.classifications)


isolate_data ='Statement: I feel lonely, i feel like I wanna talk, then I have fear of being attached, and I fear getting hurt\nEvent: hurt\n--\nStatement: I feel so lonely that I want to live with an imaginary person.\nEvent: none\n--\nStatement: I don’t have any friends. Not one. I have people who are friends with each other but I’m never, ever included in future plans.\nEvent: friends\n--\nStatement: For my whole life I\'ve struggled with loneliness. I\'m not a very normal person and I don\'t know, I just don\'t get on with a lot of people. \nEvent: none\n--\nStatement: At this point it feels like I’ve been alone for so long that whenever there are other people around, it just makes me feel anxious and nervous.\nEvent: none\n--\nStatement: I envision a relationship with anyone who shows the slightest bit of interest.Venting It never works, I always end up feeling lonelier and broken hearted.\nEvent: relationship\n--\nStatement: I feel all alone in this country\nEvent: country\n--\nStatement: I wish I had a friend.... probably a million of these posts but I just wish I had a true and genuine friend and we both had each other’s backs.\nEvent: friend\n--\nStatement: I’ve always been shy. And my parents never noticed it or if they did they didn’t care. I’ve never been close to anyone. I want to change. I want to be a good friend.\nEvent: friend\n--\nStatement: I feel alienated from my peers because of my Race\nEvent: Race\n--\nStatement: I wish I knew more people and even though I’m introverted even I want to hang out and drink and talk with people once in a while but I have only one friend and he has his own life\nEvent: friend\n--\nStatement:  I am Mexican, Japanese, and White. It feels really hard for me to relate to others of similar backgrounds. I don\'t identify with any ethnic group enough. My dad never taught me Spanish and I rarely grew up around his side of the family. \nEvent: ethnic\n--\nStatement: In the last few years I felt very lost in life and very lonely\nEvent: none\n--\nStatement: I have moved to a new country three years ago. I don\'t have friends no matter how hard I try.\nEvent: country\n--\nStatement: Since I started highschool this year i\'ve been very lonely. I have a hard time accommodating with my new classmates because i don\'t really feel like i have any connection with them.\nEvent: classmates\n--\nStatement: Over the course of my 8 year career I’ve always been the only African American in the office and the majority of my coworkers are typically middle aged white men with whom I have nothing in common with because of cultural differences. I try to initiate conversations but due to being in 2 different life stages things always feel forced. So I tend to isolate myself and focus solely on my work\nEvent: cultural\n--\nStatement: I feel cripplingly lonely almost every day now. i stay up late every night for no reason, and therefore end up being late to work almost every morning. when i do try to go to bed early all i can think about while lying in bed is how much i wish i had someone to talk to every night; someone who would want to talk to me and be with me and appreciate me for who i am.\nEvent: none\n--\nStatement: I never had a single friend my whole life. I feel extremely lonely most of the time.\nEvent: friend\n--\nStatement: I\'m stuck, I went through a period of my life when I only developed online relationships and then I realized it wasn\'t healthy so I pushed them all away and cut everybody off, people who I knew for years. But now without any online or in-person connections I feel lonely\nEvent: relationships\n--\nStatement: I have nobody and i\'m just done\nEvent: none\n--\nStatement: I\'m living alone in a small flat. Eating all alone, not watching anything, not hearing music, no one to talk to, not even by phone.\nEvent: none\n--\nStatement: My life is an endless cycle of things and I don t hang out with anyone or do anything fun.\nEvent: none\n--\nStatement: I wish I was able to have some friends\nEvent: friends\n--\nStatement: I feel so lonely\nEvent: none\n--\nStatement: I\'ve never felt so alone I recently lost my only friend, and I haven\'t made a new friend in over a decade it\'s so hard\nEvent: friend\n--\nStatement: About two years ago I moved from the US to Spain for family reasons. In this new country I work from home in English, and don\'t have the time to take any official classes. I\'ve been mostly getting by with YouTube videos and trying to figure things out as I go. However, I still feel alone in a sea of voices as I don\'t always understand what\'s being said to me, and often cannot express myself properly. I know in a few years, I\'ll get there, but that\'s a long way away. Loneliness. As I mentioned, I work from home.\nEvent: country\n--\nStatement: Just moved to a new country and I feel so alone. I’ve been here for almost 3 months and I feel so alone. I have classmates but locals tend to hang out with locals and my classmates who are from other countries like to party or do other things that I’m not really a fan of.\nEvent: country\n--\nStatement: I never realized how lonely I truly am, it\'s so hard.\nEvent: none\n--\nStatement: I have never been in a serious relationship. The one relationship that I was in I got my heart broken by a girl who after a year told me she never liked me in the first place. I\'m worried I\'ll be alone forever\nEvent: relationship\n--\nStatement: I haven\'t made a new friend in 5 years. I\'ve lost all friends except maybe one, which will end soon too anyways, since everyone likes to leave me. I\'m never going to find a relationship either, especially since having no friends is a red flag.\nEvent: friends'

stress_data = 'Statement: School is stressing me out\nEvent: School\n--\nStatement: My wife is divorcing me\nEvent: divorcing\n--\nStatement: Work is overwhelming\nEvent: Work\n--\nStatement: My work is piliing up and I feel burnt out\nEvent: Work\n--\nStatement: I witnessed my classmate having a breakdown in school\nEvent: school\n--\nStatement: My project deadline is coming up and I\'m nowhere near done\nEvent: project\n--\nStatement: I\'m stressed\nEvent: none\n--\nStatement: I got fired from my job and now I\'m worried about money\nEvent: money\n--\nStatement: I\'m feeling under the weather\nEvent: none\n--\nStatement: I feel like I have no control over my life\nEvent: none\n--\nStatement: I had the biggest mental breakdown of the day today. If I go to high school, I come home tired, loads of homework, and big eye bags. And if I miss a day I’m still tired, have loads of homework and with even bigger eye bags\nEvent: school\n--\nStatement: I am stressing out and feel like the one person I want to talk to about it with, I can’t.\nEvent: none\n--\nStatement: I am worried about starting in my new work position\nEvent: work\n--\nStatement: I\'m meeting with a work recruiter, I feel anxious and unprepared to talk with them\nEvent: work\n--\nStatement: My boyfriend is constantly stresssed about everything\nEvent: none\n--\nStatement: I\'m stressed about doing my first presentation in front of a large crowd\nEvent: presentation\n--\nStatement: I want make my family proud, I feel like I\'m letting them down and I\'m always thinking about how tiring it all is\nEvent: family\n--\nStatement: Recently I started really stressing out emotionally, compartmentalizing my stress and pushing it deep down\nEvent: none\n--\nStatement: My sister has been anxious lately, at night, even though she is exhausted, she can\'t sleep because her mind racies. She started getting sick and missing school.\nEvent: none\n--\nStatement: During these last few months of my senior year, I\'ve been more stressed than ever before. I find the idea of choosing a school to spend the next four years unbearably daunting\nEvent: school\n--\nStatement: One of the biggest stressors in my life right now is relationships\nEvent: relationships\n--\nStatement: I haven\'t been able to find an internship for the summer yet, and I\'m worried I might not be able to do so in time.\nEvent: internship\n--\nStatement: When I\'m stressed, it\'s either because of social things, like feeling like I don\'t fit in\nEvent: social\n--\nStatement: I feel so behind in school, everyone is developing cool projects for their final projects and here I am making a basic html webpage\nEvent: school\n--\nStatement: I don\'t know if I want to continue studying psychology, I\'m stressing about the future\nEvent: future\n--\nStatement: My work makes my life a living hell, stress and constant pressure\nEvent: work\n--\nStatement: I work as a nurse in a failling hospital and I take pride in my work, but it is overwhelming everyone at work including me\nEvent: work\n--\nStatement: I can\'t help anyone, everytime I try stress overwhelms me\nEvent: none\n--\nStatement: I feel unprepared for exams, I don\'t want to fail\nEvent: exams\n--\nStatement: My coworkers keep swearing at me and insulting me, it makes me anxious\nEvent: work\n--\nStatement: I\'m so stressed because of this hackathon\nEvent: hackathon\n--\nStatement: My relationship is stressing me out\nEvent: relationship\n--\nStatement: I feel stressed out\nEvent: none--\nStatement: my kid is stressing me out\nEvent: stressed'

suicide_keywords = 'Statement: I want to be dead\nEvent: none\n--\nStatement: I feel like I’m such a burden, even to my therapist\nEvent: burden\n--\nStatement: Only reason I\'m not killing myself is that my family doesn\'t deserve the pain and I can\'t be a selfish\nEvent: none\n--\nStatement: Everyday I hope I get into a car crash and die, God what I would give for my life to end.\nEvent: none\n--\nStatement: I’m done with the crying until my eyes are dry. I’m done with the casual abuse. I’m done with the fact that I feel so trapped and helpless.\nEvent: abuse\n--\nStatement: I feel like I’m suffering just to be alive. The only time I feel at peace is when I’m asleep. \nEvent: none\n--\nStatement: My fiancé just took his life because of his mental illness. He had depression and anxiety disorder. Now I think he had passed his agony and his illness to me. I’m very suicidal every morning. I miss him so much. I’m in so much pain from the colossal loss.\nEvent: loss\n--\nStatement: I\'m so tired of being alive. I think my days are always bad. I hate my life. I wish I was dead\nEvent: none\n--\nStatement: I know that from today its going to keep getting worse.What the fuck is even the point anymore\nEvent: none\n--\nStatement: ’I have been unemployed for 8 months now I been laying around for that long and my parents want me out the house because they don’t believe anything I say and they think I’m just being lazy when I actually drowning in pain\nEvent: parents\n--\nStatement: Everyday I’ve been struggling with the thought of suicide. TL/DR. I go to work everyday come home to a girlfriend who wants nothing to do with me. I try my best to be involved but the kids just want their mother, and she just wants to do whatever she can to avoid me or be as little possible interested in me at all.\nEvent: girlfriend\n--\nStatement: I used to live with my father years ago, but when he did, he would sexually assault me. I\'m so scared because if he starts living with us again he might start doing those things again. Everything is going to hell and I dont know what to do or how long I can do this for. I dont want to be here. I hate this.\nEvent: father\n--\nStatement: My life is a mess. I want to die. I am lonely yet I don\'t know how to talk and don\'t really want to (if it makes sense). I am very stupid, I can\'t do my job well, I can\'t focus, can\'t remember anything and think logically.\nEvent: none\n--\nStatement: i want to kill myself so badly. i don\'t have any friends.\nEvent: friends\n--\nStatement: I have a lot wrong with my life, most of which is my fault, usually because of negligence. My wife had an affair. I\'m about to lose my house. Job that doesn\'t pay nearly enough. Can\'t even think of a job I could get that could support my family.\nEvent: pay\n--\nStatement: I’ve had severe depression and struggled with self harm and suicidal ideation since I was around 10. And now that I’m an adult, it’s harder than ever to handle. Not only am I suicidal, but I have to wake up, go to work and act normal for customers who scream in my face all day, come home and panic about college and student loans.\nEvent: none\n--\nStatement: I already wanna die. I’ve been like this since I\'ve never told anyone because I\'m uncertain what goes on in my head. I feel like I’m just gonna make a fool of myself like I always do when I try to explain my feelings or my mind but in reality I don’t even know what’s going on in my head.\nEvent: uncertain\n--\nStatement: There are so many days in my life that i just wish i\'d not been alive. i just wish i would die. I wish I could talk to someone about all my problems but i\'m always worried to because i worry if they will ask me something\nEvent: none\n--\nStatement: I don\'t enjoy life anymore, I am short, losing my hair my old hobbies don\'t give me joy and I’m a lazy failure\nEvent: failure\n--\nStatement: So at the start of the year I started to sense that mine and my boyfriends relationship wasn’t working out so I shut down,broke up with him and pushed all of my friends away and now as we approach the end of the year I have nobody I have no friends at all and my ex is dating someone else and all I do is cry all day and when I say cry all day I literally mean I cry all day and sometimes tears don’t even come out. I’m at a point now where I can’t see the reason to keep living\nEvent: relationship\n--\nStatement: My best friend of five years hates me. She has me blocked. She responded to one of my vents about my horrible financial situation with a picture of one of our teachers. She called me a dumbass. She invalidated me. She made me feel inferior.and it’s not just her. All of my friends hate me. They think I’m annoying.\nEvent: friends\n--\nStatement: I do want to die, I don’t care who will miss me or how much they would. I guess I’m selfish. I have no one to talk to and I can’t even talk to my mom because I would be embarrassed. Sometimes I fantasize how I would commit suicide and how it would effect people.\nEvent: none\n--\nStatement: I give up. I can’t wait to leave, there\'s nothing for me here.\nEvent: none\n--\nStatement: I\'m so sad and tired of living. I\'m only 20. No one told me life is going to be so shitty. I don\'t live to work, I work to stay alive. Everything is so expensive, I can\'t even pay my rent... But I\'m not going to be homeless, especially when winter is coming. I will hang myself.\nEvent: expensive\n--\nStatement: I have been having suicidal thoughts for more than 2 months now. I actually having underlying depression + anxiety since 9 years ago after both my parents diagnosed with cancer\nEvent: cancer\n--\nStatement: I have begun to plan for my suicide attempt and I am ashamed to admit that I am looking forward to it. After such an extended period of anhedonia I am finally going to put an end to the anguish and suffering that I\'ve been going through for the past few years.\nEvent: anhedonia\n--\nStatement: I feel so fucked up. I want to die. I don\'t want to do this anymore. My closest friends are moving tomorrow, it’s something I’ve been dreading for a very long time now. They’re the last of my friends still around, and spending time with them once a week has been the one thing keeping me alive for so long now.\nEvent: friends\n--\nStatement: Any one else get suicidal when they work certain jobs? I feel ridiculous and like I can\'t explain it to anyone who\'d get it. I was fine when I wasn\'t working but then I started working a corporate office job full time and over the last couple of months, the thoughts have been getting increasingly worse.\n\nEvent: work\n--\nStatement: I can\'t keep going. I\'m a shell of what I used to be, mentally abused and cheated on by the only person I ever wanted a future with.\nEvent: future\n--\nStatement: I failed my life, and I\'m too tired to be wanting to put in the effort to fix it. I\'ve done so much bad shit to people. I\'d feel better with myself if I tried to kill myself tomorrow.\nEvent: failed\n--\nStatement: I want to commit suicide\nEvent: none'

def keyword_extract(extract_statement: str, training_data: str):
    string_formatted = '\n--\nStatement: '+extract_statement+'\nEvent:'
    response = co.generate(
      model='small',
      prompt=training_data+string_formatted,
      max_tokens=10,
      temperature=0.3,
      k=0,
      p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stop_sequences=["--"],
      return_likelihoods='NONE')
    return str('{}'.format(response.generations[-1].text))


#demo input for the users inputting what they're feeling
def test_cat(csv_name: str):
    inputmessage = input('Input string: ')
    category = str(senti_analysis(inputmessage, csv_name))
    cause = str(keyword_extract(inputmessage))
    cause = cause.replace('\n', '')
    cause = cause.replace('--', '')
    return (predic_confid(category), cause.strip())


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
      max_tokens=60,
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


def link_story(perspective: str, issue_type: str, cause: str):
    perspectives = ['second', 'first', 'positive']
    other_perspec_index = perspectives.index(perspective)
    #perspective will never be positive as they're posting
    other_perspec = perspectives[other_perspec_index+1]
    #read the positive story csv ignore the story itself as it's not needed now
    stories = read_csv(positive_story)
    #array that will hold the location of the 3 stories that best match the user
    best_stories = []
    for i in range(len(stories[0])):
        #best case is two matching tags
        if issue_type == stories[0][i] and cause == stories[1][i]:
            best_stories.append(i)
    #second best is just a matching issue but different cause if list isn't top3
    for i in range(len(stories[0])):
        if issue_type == stories[0][i] and i not in best_stories and len(best_stories) < 3:
            best_stories.append(i)
    return (best_stories)


def read_chat(messages: list, summarize: bool):
    # checking if the first message is vague
    first_message = str(messages[0])
    vague = check_vague(first_message)
    vague = vague[0]
    vague = vague != 'specific'
    # vague is now a True or False
    # now check whether we can isolate the cause of their stress
    cause = str(keyword_extract(first_message, stress_data))
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
        data = []
        if myfirstanswer=="positive":
            data.append(request.form["oField1"])
            data.append(request.form["oField2"])
        elif myfirstanswer=="negative":
            data.append(request.form["feelings"])
            ifVague = read_chat(data, False)
            answer1 = predic_confid(str(senti_analysis(request.form["feelings"], './static/issues_and_situations.csv')))
            if answer1[0]=='suicidal':
                dataset = suicide_keywords
            if answer1[0]=='isolated':
                dataset = isolate_data
            if answer1[0]=='stressed':
                dataset = stress_data          
        return render_template('form2.html', ifVague=ifVague, feelings=request.form["feelings"], check=answer1, data=keyword_extract(request.form["feelings"], dataset))
    return render_template('index.html', data="nothing")

@app.route('/check_data', methods=['GET', 'POST'])
def check_data():
    if request.method == 'POST':
        message = []
        if request.form["check"]=="suicidal" or request.form["check"]=="isolated":
            if request.form["share"] == "yes":
                return render_template('form3.html')
        message.append(request.form["feelings"])
        message.append(request.form["environment"])
        message.append(request.form["howEnv"])
        message.append(request.form["elaborate"])
        message.append(request.form["effects"])
        message.append(request.form["obstacles"])
        answer1 = read_chat(message, True)
        return render_template('index.html', data=answer1)
    else:
        data = "Nothing"
    return render_template('index.html', data=data)



if __name__ == '__main__':
    app.run(debug=1)