import praw
import time
import json
from threading import Thread

with open('./config.json') as json_data_file: # Load config file
    config = json.load(json_data_file)

removalText = """
**Unfortunately, we've had to remove your post.**
___


### Post Flair Guidelines

We require all users to set a post flair for their own post. There is a 30 minute grace period, and this has passed for this post. 

Don't know how to flair your post? Click [here](http://imgur.com/a/m3FI3) to view this helpful guide on how to flair your post. 

For more information, please read [this post](https://www.reddit.com/r/FortNiteBR/comments/8bznpy/state_of_the_subreddit_new_moderators_survey/).


___
[**Here are our subreddit rules.**](https://www.reddit.com/r/FortNiteBR/wiki/rules) - If you have any queries about this, you can contact us via [Moderator Mail](https://www.reddit.com/message/compose?to=%2Fr%2FFortNiteBR).
"""

class FortniteOverlord:
    def __init__ (self):
        
        self.reddit = self.login() # Run the function to login to reddit

        self.postStorage = list() # Initalize the storage for posts

        (Thread(target = self.getPosts)).start() # Start getting posts on a seperate thread
        (Thread(target = self.checkFlair)).start() # Start processing posts on a seperate thread

    def login(self):
        self.loginTime = time.time() # Define when the bot was logged in

        return praw.Reddit( # Login to reddit with details
            client_id=config['reddit']['id'],
            client_secret=config['reddit']['secret'],
            user_agent=config['reddit']['agent'],
            username=config['reddit']['username'],
            password=config['reddit']['password']
        )
    
    def getPosts(self):        
        for post in self.reddit.subreddit('fortnitebr').stream.submissions(): # Get submissions when posted in specified subreddit
            
            if post.created_utc - self.loginTime > 0: # Make sure the post is from after the bot started (Helps prevent double moderation)
                self.postStorage.append({'key': post.id, 'time': post.created_utc}) # Add post to storage
    
    def checkFlair(self):
        while True:
            filtered = filter(lambda x: x['time'] + 30 * 60 - time.time() < 0, self.postStorage) # Filter out all posts that are not older than 30 minutes

            for data in filtered:
                
                post = self.reddit.submission(data['key']) # Get the submission from reddit

                self.postStorage.remove(data) # Remove the post from the bot's cache before doing anything, in order to prevent double moderation

                if (post.link_flair_text is None): # Check if the flair doesn't exist

                    (post.reply(removalText)).mod.distinguish(how='yes', sticky=True) # Reply with the removal reason and then distinguish/sticky the comment
                    post.mod.remove() # Remove the original post
                    post.mod.lock() # Lock the original post

                    print('Post Removed: {} | {}'.format(post.id, time.time())) # Log that a post was removed

FortniteOverlord()
