#!/usr/bin/env python
import json
import urllib2

# Get the latest 'Who is hiring?' thread ID
def who_is_hiring_thread():
    # optionally, you can override the calculation with a specific post.
    post_id = os.environ.get("HN_POST_ID", None)
    if post_id:
        return str(post_id)

    try:
        x = urllib2.urlopen('https://hacker-news.firebaseio.com/v0/user/whoishiring.json')
        data = json.loads(x.read())
        x.close()
        # Always get the 3rd most recent submission. The API returns the posts
        # in chronological order, starting with the newest. The whoishiring 'bot
        # creates the Who is Hiring thread, then freelancer, then who's looking
        # thread in that order. Thus, the most recent thread ID is the who's
        # looking thread and 2nd ID in the list is the freelancer thread.
        #
        # For my purposes, ignore those last two and only focus on the Who is
        # Hiring thread.
        return str(data['submitted'][2])
    except Exception as error:
        print type(error), error

if __name__ == '__main__':
    print who_is_hiring_thread()
