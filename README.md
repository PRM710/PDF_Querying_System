#Things need to run this project

# environment variables
/src/.env

#Your env file shoud look like this

AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=your-default-region
OPENAI_API_KEY=your-openai-api-key

#key file of firebase
/src/key.json   #key.json file you will find it in Firebase Project settings -> Service Account -> generate new private key

# Libraries required to install to run this project

Install required libraries -
    For python flask install following libraries using 'pip install library-name' in one terminal  -
       -Flask
       -Flask-CORS
       -python-dotenv
       -boto3
       -firebase-admin
       -PyMuPDF
       -openai
       -axios
   (I will provide its requirements.txt file just hit 'pip install -r requirements.txt' in terminal it will automaticall install all the required libaries..)
   
For react install following things in another terminal -
       - bash "npm install react react-dom react-scripts"


#To run this project

1) In one terminal hit -
   - 'cd src'
   - 'python app.py'
     
2) In another terminal hit -
   - npm run
   - Open the given link in the terminal or it will automatically run the browser.


Thats it our application will run perfectly!

Thank You!






