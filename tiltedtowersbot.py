import praw
from prawcore import PrawcoreException
import time
import json
from threading import Thread

no_flair_removal = """
**Unfortunately, we've had to remove your post.**
___


### Post Flair Guidelines

We require all users to set a post flair for their own post. There is a 30 minute grace period, and this has passed for this post. 

Don't know how to flair your post? Click [here](http://imgur.com/a/m3FI3) to view this helpful guide on how to flair your post. 

For more information, please read [this post](https://www.reddit.com/r/FortNiteBR/comments/8bznpy/state_of_the_subreddit_new_moderators_survey/).


___
[**Here are our subreddit rules.**](https://www.reddit.com/r/{}/wiki/rules) - If you have any queries about this, you can contact us via [Moderator Mail](https://www.reddit.com/message/compose?to=%2Fr%2F{})."""

suggestion_removal = """
**Unfortunately, we've had to remove your post.**
___


### Suggestion Link Posts

We do not allow suggestions to be link posts on /r/FortniteBR. We require them to be made as text posts with context to describe your suggestion. Sites such as Gfycat, Streamable or Imgur can be used to upload images or videos in your text post.


___
[**Here are our subreddit rules.**](https://www.reddit.com/r/{}/wiki/rules) - If you have any queries about this, you can contact us via [Moderator Mail](https://www.reddit.com/message/compose?to=%2Fr%2F{})
"""

class TiltedTowersBot:
    def __init__(self):
        self.start_time = time.time()
        self.reddit = self.login()
        print('--- logged in to reddit')

        self.post_storage = []
        self.thread_storage = {}
        print('--- storage initalized')

        for sub in config['reddit']['subreddits']:
            self.thread_storage[sub] = Thread(target=self.get_posts, args=[sub])
            self.thread_storage[sub].start()

        Thread(target=self.check_flair).start()
        print(f'--- {len(self.thread_storage)} threads started and stored')
        print('--- post processing started')

    def login(self):
        return praw.Reddit(
            client_id=config['reddit']['id'],
            client_secret=config['reddit']['secret'],
            user_agent=config['reddit']['agent'],
            username=config['reddit']['username'],
            password=config['reddit']['password']
        )

    def get_posts(self, sub):
        try:
            for post in self.reddit.subreddit(sub).stream.submissions():
                if post.created_utc - self.start_time > 0:
                    self.post_storage.append({'key': post.id, 'sub': sub, 'time': post.created_utc})
        except PrawcoreException as e:
            print(f'exception: {e}')

    def check_flair(self):
        while True:
            try:
                filtered = filter(lambda x: x['time'] + 30 * 60 - time.time() < 0, self.post_storage)

                for data in filtered:
                    post = self.reddit.submission(data['key'])
                    self.post_storage.remove(data)

                    if post.link_flair_text is None or post.link_flair_css_class is None:
                        post.reply(no_flair_removal.format(data['sub'], data['sub'])).mod.distinguish(how='yes', sticky=True)
                        post.mod.remove()
                        post.mod.lock()
                        print(f'post removed (no flair): {post.id} | {time.time()}')

                    elif post.subreddit.display_name == 'FortNiteBR' and post.is_self == False and post.link_flair_css_class == 'suggestion':
                        post.reply(suggestion_removal.format(data['sub'], data['sub'])).mod.distinguish(how='yes', sticky=True)
                        post.mod.remove()
                        post.mod.lock()
                        print(f'post removed (link suggestion): {post.id} | {time.time()}')
                    else:
                        print(f'all checks passed: {post.id} ({post.subreddit.display_name}, {post.domain}, {post.link_flair_css_class})')

            except PrawcoreException as e:
                print(f'exception: {e}')


if __name__ == '__main__':
    with open('./config.json') as config_file:
        config = json.load(config_file)
    TiltedTowersBot()
