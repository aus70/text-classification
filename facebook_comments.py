# Please refer to https://github.com/alessandrousseglioviretta/text-classification/wiki/Facebook-comments-classification
# for a full explanation of this code

#  Print the 100 most recent comments
import requests
import simplejson as json

FACEBOOK_GRAPH_COMMENTS_URL = 'https://graph.facebook.com/comments/'
params = {'id': '10151435566046749', 'limit': 100}  # Comments on one of Barack Obama's Facebook posts
response = requests.get(FACEBOOK_GRAPH_COMMENTS_URL, params=params)
print json.dumps(response.json(), indent=4 * ' ')
comments = response.json()


# Save the comments into a Comma-Separated-Values (CSV) file
import csv

with open('facebook_comments.csv', 'wb') as csvfile:
    comment_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for comment in comments['data']:
        print comment['message']
        message = comment['message'].encode('utf-8').strip()
        comment_writer.writerow(['class label', message])


# Train a classification model
import time

SERVER = 'https://stc.p.mashape.com'
TEST_MODEL_NAME = 'test_model_1'
FORMAT = {'SERVER': SERVER, 'TEST_MODEL_NAME': TEST_MODEL_NAME}
TEST_TRAINING_FILE = 'facebook_comments.csv' # You need to manually label the comments before training the classifier
HEADERS = {'X-Mashape-Authorization': '<your own authorization key>'}
response = requests.post('%(SERVER)s/%(TEST_MODEL_NAME)s/train' % FORMAT,
                        files={'file': open(TEST_TRAINING_FILE, 'r')}, headers=HEADERS)


# Wait for the training to complete.
SLEEP_TIME = 10
MAX_TIME = 300
elapsed_time = 0
while True:
    if elapsed_time > MAX_TIME:
        raise Exception('Training Error: Training is taking too much time')
    response = requests.get('%(SERVER)s/%(TEST_MODEL_NAME)s/status' % FORMAT, headers=HEADERS)
    assert response.status_code == 200
    trainingStatus = response.json()['trainingStatus']
    print('Elapsed time: ' + str(elapsed_time) + ' Training status: ' + trainingStatus)
    if trainingStatus == 'DONE':
        break
    elif trainingStatus == 'RUNNING':
        time.sleep(SLEEP_TIME)
        elapsed_time += SLEEP_TIME
        continue
    else:
        raise Exception('Training Error: ' + trainingStatus)
print('Training completed')


# Get full information about the trained model
response = requests.get('%(SERVER)s/%(TEST_MODEL_NAME)s/analysis' % FORMAT, headers=HEADERS)
assert response.status_code == 200
print response.text


# Classify a short sentence
headers = HEADERS
headers['content-type'] = 'application/json'
payload = json.dumps({'text': "that's great!"})
response = requests.post('%(SERVER)s/%(TEST_MODEL_NAME)s/classify' % FORMAT, data=payload, headers=headers)
assert response.status_code == 200
print response.text
