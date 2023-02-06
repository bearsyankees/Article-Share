
# SquibLib
This is the code powering the half-baked article sharing social media platofrm [squiblib.com](https://www.squiblib.com).

## Languages/Libraries/Other Tech Used

Python

Flask

SQLAlchemy

Heroku



## What is it?

SquibLib started as a way for me to kill two birds with one stone -- learn how to do secure user 
authentication on the web, and a way to organize all of the articles sent continuously
in my family iMessage groupchat. SquibLib allows you to join groups after creating an account, and 
when you want to share an article with that group you can easily paste the article link in, give it a genre and comments if you want,
and other members of your group will be able to see it. They will get an email notification (if they have that setting on),
or will see it when they navigate to your groups feed.

## How does it work?

SquibLib runs using the Flask framework and a SQL DB. Passwords are totally encrypted.
Mail is sent using smtp and Flask mail.