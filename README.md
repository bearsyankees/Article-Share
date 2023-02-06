
# SquibLib
This is the code powering the prototype for an article sharing social media platform [squiblib.com](https://www.squiblib.com).

## Languages/Libraries/Other Tech Used

Python

Flask

SQLAlchemy

Heroku



## What is it?

SquibLib started as a way for me to kill two birds with one stone: learn how to do secure user authentication on the web, and create a way to better organize all of the articles sent continuously in my family iMessage groupchat. 

After creating an account on SquibLib, a user can select groups to join and then read and share articles in that group. The user interface right now is simple and straightforward: to post an article, a user just pastes the article link in the box, associates a genre with it and optionally adds comments explaining the topic of the article or why it might be interesting to fellow group members, etc. All other members of the group will see it, either by navigating directly to the feed of the group or via receipt of an email notification of a new post (controlled by a setting in the site.)
 
My family has found it very handy.  It has eased the endless scrolling in iMessage while trying to find an article shared from weeks ago!

## How does it work?

SquibLib runs using the Flask framework and a SQL DB. Passwords are totally encrypted.
Mail is sent using smtp and Flask mail.
