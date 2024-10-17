from flask import Flask, request, jsonify, render_template, session
import nltk
from nltk.chat.util import Chat, reflections
import os
from datetime import datetime
import logging
import re


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Configure logging for errors
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Define pairs of patterns and responses
pairs = [
    # Greetings and Basic Information
     [r'(?i)\b(hi|hello|hey)\b', [
        'Hello! How can I assist you with our university courses today?',
        'Hi there! What information about our courses are you looking for?',
        'Hey! I\'m EduBot. How can I help you with our educational offerings?',
        'Greetings! Let me know how I can help you with our university programs.',
        'Hi! What would you like to know about our courses today?',
        'Hello! Ready to explore our wide range of university courses?',
        'Hey there! How can I support your educational journey today?',
        'Hi! Interested in learning more about our courses? I\'m here to help!',
        'Good day! How can I assist you with our academic programs?',
        'Welcome! What would you like to learn about our university courses?',
        'Howdy! Looking for information on our courses? I\'m here to help!',
        'Salutations! How may I assist you with our educational offerings?',
        'Hiya! What can I do for you regarding our university courses?',
        'Hello there! Need help with course information? I\'m at your service!',
        'Hey! Excited to help you explore our university programs. How can I assist?',
        'Hello! What subjects are you interested in today?',
        'Hi! Let\'s find the perfect course for your academic goals.',
        'Hey! Ready to dive into our course offerings? How can I help?',
        'Greetings! Looking for specific courses or general information?',
        'Hi! How can I make your search for university courses easier today?',
    ]],

    [r'(?i)what is your name\??', ['I am EduBot, your assistant for university course information.']],
    [r'(?i)\b(goodbye|bye|see you later)\b', ['Goodbye! Feel free to reach out if you have more questions about our courses.']],
    
    # Course Offerings
    [r'(?i)what courses (do you offer|are you offering|can you offer|provide|have)\??', [
        'We offer a wide range of university-level courses in Engineering, Business, Arts, Sciences, and Humanities. Which department are you interested in?'
    ]],
    [r'(?i)list (all )?courses you offer', [
        'Certainly! We offer courses in Engineering, Business, Arts, Sciences, and Humanities. Which department would you like to know more about?'
    ]],
    
    # Department-specific Inquiries
    # Engineering
    [
        r'(?i)tell me about (the )?Engineering department',
        [
            'Our Engineering department offers courses in Mechanical Engineering, Electrical Engineering, Civil Engineering, Computer Engineering, Software Engineering, and more. Would you like details on a specific program?'
        ]
    ],
    # Career Opportunities after Engineering
    [
        r'(?i)what career opportunities are available after completing an Engineering degree\??',
        [
            'Graduates from our Engineering programs have career opportunities in industries like automotive, aerospace, civil infrastructure, software development, telecommunications, and more. Would you like to know about specific job roles or companies hiring our graduates?'
        ]
    ],
    
    # Core Subjects in Engineering Programs
    [
        r'(?i)what are the core subjects in Engineering programs\??',
        [
            'The core subjects in our Engineering programs typically include mathematics, physics, materials science, computer programming, and specialized courses related to the chosen discipline such as mechanics, electronics, or software development. Would you like to know more about elective subjects?'
        ]
    ],
    
    # Specializations within Engineering
    [
        r'(?i)can i specialize in a particular field within Engineering\??',
        [
            'Yes, our Engineering programs offer specializations in fields such as Artificial Intelligence, Data Science, Cybersecurity, Robotics, and Renewable Energy. Would you like to know about the requirements or curriculum for a specific specialization?'
        ]
    ],
    
    # Business Department Inquiries
    [r'(?i)can you provide information about the Business programs\??', [
        'Our Business programs include courses in Management, Marketing, Finance, Entrepreneurship, and more. Each course is designed to provide practical skills and theoretical knowledge. Would you like to know more about a specific program?'
    ]],
    
    # General Admission Process
    [r'(?i)how can i apply or enroll in a course\??', [
        'You can apply or enroll by visiting our university\'s admission portal. The process typically involves selecting your program, filling out the application form, submitting required documents, and completing the payment. Would you like me to guide you through the steps or provide the link?'
    ]],
    
    # Course Prerequisites
    [r'(?i)what are the prerequisites for your courses\??', [
        'The prerequisites for our courses depend on the program and the level of study. Typically, a background in the relevant subject and foundational knowledge in mathematics or science is required. Would you like details on prerequisites for a specific program?'
    ]],
    
    # Online Courses
    [r'(?i)are online courses available\??', [
        'Yes, we offer a wide range of online courses to provide flexibility for our students. You can access course materials, lectures, and assignments online. Would you like to know more about the online programs we offer?'
    ]],
    
    # Financial Aid and Scholarships
    [r'(?i)are there scholarships or financial aid options available\??', [
        'Yes, we offer scholarships and financial aid based on merit and need. You can find more information on our scholarships page. Would you like to know more about the eligibility criteria?'
    ]],
    
    # Internship Opportunities
    [r'(?i)are internships available for students\??', [
        'Yes, we offer internship opportunities for students across different programs. These internships are designed to provide practical experience and industry exposure. Would you like to know more about how to apply for internships?'
    ]],
    
    # Business
    [r'(?i)tell me about (the )?Business department', [
        'Our Business department offers courses in Management, Marketing, Finance, Entrepreneurship, and more. Which area are you interested in?'
    ]],
    [r'(?i)tell me about (Management|Marketing|Finance|Entrepreneurship)', [
        lambda matches: {
            'Management': 'Management courses cover organizational behavior, strategic planning, and leadership skills. These courses are designed to prepare you for managerial roles in various industries. Would you like to learn about the program structure?',
            'Marketing': 'Marketing courses cover market research, consumer behavior, digital marketing, and brand management. These courses aim to equip you with skills to excel in marketing roles. Would you like to know about the curriculum?',
            'Finance': 'Finance courses include financial analysis, investment strategies, corporate finance, and risk management. These courses prepare you for careers in finance and banking. Would you like to know about admission requirements?',
            'Entrepreneurship': 'Entrepreneurship courses focus on business planning, startup management, innovation, and venture capital. These courses are designed for aspiring entrepreneurs. Would you like to learn about the program structure?'
        }[matches.group(1)]
    ]],
    
    # Arts
    [r'(?i)tell me about (the )?Arts department', [
        'The Arts department offers courses in Fine Arts, Graphic Design, Performing Arts, and more. Which discipline interests you?'
    ]],
    [r'(?i)tell me about (Fine Arts|Graphic Design|Performing Arts)', [
        lambda matches: {
            'Fine Arts': 'Fine Arts courses include painting, sculpture, and visual arts. These courses aim to develop your creative and technical skills. Do you want to know about the application process?',
            'Graphic Design': 'Graphic Design courses cover visual communication, typography, digital media, and branding. These courses prepare you for careers in design and advertising. Would you like more information?',
            'Performing Arts': 'Performing Arts courses include acting, dance, music, and theater production. These courses are designed to enhance your performance and production skills. Would you like to know about the curriculum?'
        }[matches.group(1)]
    ]],
    
    # Sciences
    [r'(?i)tell me about (the )?Sciences department', [
        'Our Sciences department offers courses in Physics, Chemistry, Biology, Environmental Science, and more. Which field are you interested in?'
    ]],
    [r'(?i)tell me about (Physics|Chemistry|Biology|Environmental Science)', [
        lambda matches: {
            'Physics': 'Physics courses cover mechanics, electromagnetism, quantum physics, and astrophysics. These courses are designed to deepen your understanding of the fundamental principles governing the universe. Need more details on course offerings?',
            'Chemistry': 'Chemistry courses include organic chemistry, inorganic chemistry, physical chemistry, and analytical chemistry. These courses provide a comprehensive understanding of chemical processes. Would you like to know about the curriculum?',
            'Biology': 'Biology courses cover molecular biology, genetics, ecology, and biotechnology. These courses aim to expand your knowledge of living organisms. Do you need information on admission requirements?',
            'Environmental Science': 'Environmental Science courses focus on ecosystem management, sustainability, and environmental policy. These courses prepare you to address environmental challenges. Would you like more details?'
        }[matches.group(1)]
    ]],
    
    # Humanities
    [r'(?i)tell me about (the )?Humanities department', [
        'The Humanities department offers courses in Philosophy, Sociology, Psychology, History, and more. Which subject would you like to explore?'
    ]],
    [r'(?i)tell me about (Philosophy|Sociology|Psychology|History)', [
        lambda matches: {
            'Philosophy': 'Philosophy courses explore fundamental questions about existence, knowledge, ethics, and logic. These courses aim to enhance your critical thinking and analytical skills. Interested in course prerequisites?',
            'Sociology': 'Sociology courses cover social behavior, institutions, cultural norms, and social research methods. These courses prepare you to analyze societal structures. Would you like more information?',
            'Psychology': 'Psychology courses include cognitive psychology, behavioral psychology, clinical psychology, and developmental psychology. These courses aim to understand human behavior and mental processes. Do you need details on admission requirements?',
            'History': 'History courses cover ancient civilizations, modern history, historical research methods, and specialized topics. These courses are designed to deepen your understanding of historical events and contexts. Would you like to know about the curriculum?'
        }[matches.group(1)]
    ]],
    
    # Enrollment Process
    [r'(?i)how can i (enroll|register) in (a )?course\??', [
        'You can enroll in a course by visiting our enrollment page and selecting the course you\'re interested in. Do you need the enrollment link?'
    ]],
    [r'(?i)enroll me in a course', [
        'Sure! Please visit our enrollment page to register for courses. Here is the link: https://www.education.com/enroll'
    ]],
    [r'^(?i)(yes|sure|absolutely|of course)$', [
        'Great! Here is the enrollment link: https://www.education.com/enroll'
    ]],
    [r'(?i)\b(no|nope|not really)\b', [
        'No problem! If you have any other questions about our courses, feel free to ask.'
    ]],
    
    # Prerequisites
    [r'(?i)what are the prerequisites for (.+)\??', [
        lambda matches: f'The prerequisites for {matches.group(1)} include a basic understanding of related subjects and a willingness to learn. Would you like more details on specific courses?'
    ]],
    
    # Resources
    [r'(?i)can you recommend resources for (.+)\??', [
        lambda matches: f'Sure! Here are some great resources for {matches.group(1)}:\n1. [Resource 1](https://www.resource1.com)\n2. [Resource 2](https://www.resource2.com)\n3. [Resource 3](https://www.resource3.com)'
    ]],
    
    # Schedule Information
    [r'(?i)what is the schedule for (.+)\??', [
        lambda matches: f'The schedule for {matches.group(1)} is available on our website under the course details section. Would you like me to send you the link?'
    ]],
    
    # Instructor Information
    [r'(?i)who is the instructor for (.+)\??', [
        lambda matches: f'The instructor for {matches.group(1)} is Professor Smith, who has extensive experience in the field. Would you like to know more about their background?'
    ]],
    
    # Fees Information
    [r'(?i)what are the fees for (.+)\??', [
        lambda matches: f'The fees for {matches.group(1)} vary depending on the level and duration of the course. You can find detailed pricing on our courses page. Do you need the link?'
    ]],
    
    # Certification
    [r'(?i)can i get a certificate after completing (.+)\??', [
        lambda matches: f'Yes, you will receive a certificate upon successfully completing {matches.group(1)}.'
    ]],
    
    # Curriculum Details
    [r'(?i)what does the curriculum for (.+) include\??', [
        lambda matches: f'The curriculum for {matches.group(1)} includes a mix of theoretical lectures, practical labs, and project-based assignments designed to provide a comprehensive understanding of the subject. Would you like to see a detailed syllabus?'
    ]],
    
    # Admission Requirements
    [r'(?i)what are the admission requirements for (.+)\??', [
        lambda matches: f'Admission requirements for {matches.group(1)} typically include a high school diploma, transcripts, letters of recommendation, and a personal statement. Specific requirements may vary by program. Need more detailed information?'
    ]],
    
    # Application Deadlines
    [r'(?i)what are the application deadlines for (.+)\??', [
        lambda matches: f'Application deadlines for {matches.group(1)} are listed on our admissions page. It\'s best to apply early to secure your spot. Would you like the link to the admissions page?'
    ]],
    
    # Online Courses
    [r'(?i)are there online courses available for (.+)\??', [
        lambda matches: f'Yes, we offer online courses for {matches.group(1)} to provide flexibility for our students. You can find more information on our online learning page. Would you like the link?'
    ]],
    
    # Scholarships and Financial Aid
    [r'(?i)do you offer scholarships for (.+)\??', [
        lambda matches: f'Yes, we offer several scholarships for {matches.group(1)} based on academic merit and financial need. You can find more details on our financial aid page. Need the link?'
    ]],
    
    # Internship Opportunities
    [r'(?i)are there internship opportunities in (.+)\??', [
        lambda matches: f'Yes, our {matches.group(1)} program includes internship opportunities with leading companies to provide practical experience. Would you like to know how to apply?'
    ]],
    
    # Career Prospects
    [r'(?i)what career prospects do i have after completing (.+)\??', [
        lambda matches: f'After completing {matches.group(1)}, you can pursue careers in various industries such as [Industry 1], [Industry 2], and [Industry 3]. Would you like more detailed information?'
    ]],
    
    # Student Support
    [r'(?i)what kind of support do you offer to students in (.+)\??', [
        lambda matches: f'We offer comprehensive support for students in {matches.group(1)}, including academic advising, tutoring services, and career counseling. Do you need more information on these services?'
    ]],
    
    # Facilities
    [r'(?i)what facilities are available for (.+)\??', [
        lambda matches: f'Our facilities for {matches.group(1)} include state-of-the-art labs, libraries, collaborative workspaces, and dedicated study areas. Would you like a virtual tour link?'
    ]],
    
    # Graduation Requirements
    [r'(?i)what are the graduation requirements for (.+)\??', [
        lambda matches: f'Graduation requirements for {matches.group(1)} include completing all required coursework, maintaining a minimum GPA, and successfully completing a capstone project or thesis. Need more details?'
    ]],
    
    # Enrollment Steps
    [r'(?i)what are the steps to enroll in (.+)\??', [
        lambda matches: f'To enroll in {matches.group(1)}, follow these steps:\n1. Visit our enrollment page.\n2. Select the {matches.group(1)} course.\n3. Fill out the enrollment form.\n4. Submit necessary documents.\n5. Complete payment.\nWould you like the enrollment page link?'
    ]],
    
    # Additional General Help Related to Courses
    [r'(?i)i need help with (.+)', [
        lambda matches: f'Sure, I can help you with {matches.group(1)}. Are you looking for information on course selection, enrollment, or something else?'
    ]],
    
    # Unrecognized Queries Related to Courses
    [r'(?i)(.*)', [
        'I\'m here to help you with our university courses. Could you please specify your question or choose from the following topics: course offerings, enrollment, prerequisites, schedule, fees, or instructors?'
    ]],
]

# Initialize the chatbot
chatbot = Chat(pairs, reflections)

def generate_response(message):
    response = chatbot.respond(message)
    return response if response else "I don't understand. Can you rephrase?"

@app.route('/')
def home():
    # Initialize conversation log in session if not present
    if 'conversation' not in session:
        session['conversation'] = []
    return render_template('index.html')

@app.route('/courses')
def courses():
    if 'conversation' not in session:
        session['conversation'] = []
    return render_template('courses.html')

@app.route('/about')
def about():
    if 'conversation' not in session:
        session['conversation'] = []
    return render_template('about.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.form['message'].strip()
        if not user_message:
            return jsonify({'response': "Please enter a message."})

        # Generate bot response
        response = generate_response(user_message)

        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update session conversation
        session['conversation'].append({
            'sender': 'You',
            'message': user_message,
            'timestamp': timestamp
        })
        session['conversation'].append({
            'sender': 'Bot',
            'message': response,
            'timestamp': timestamp
        })

        # Optionally log the conversation to a file
        with open("conversation_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} You: {user_message}\n{timestamp} Bot: {response}\n")

        return jsonify({'response': response, 'timestamp': timestamp})
    except Exception as e:
        logging.error(f"Error in /chat route: {e}")
        return jsonify({'response': "An error occurred. Please try again.", 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})



@app.route('/clear', methods=['POST'])
def clear():
    session.pop('conversation', None)
    # Optionally clear the log file
    # with open("conversation_log.txt", "w") as log_file:
    #     log_file.write("")
    return jsonify({'response': "Chat cleared."})

if __name__ == '__main__':
    app.run(debug=True)
