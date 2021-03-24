# Software Contribution to Society
---

## Purpose
---
Email has been an essential for almost every in the sociey whether for sending formal messages to other peoeple through the internet or as account holding for platforms.
While Gmail being the biggest platform for email users, almost every person have a google account and gmail has been a tool that can't be left aside.

As eldery people are not as proficient at technologies or are having trouble discovering the features of gmail's user interface, it becomes a barrier for them to get familiar with it.
We have decided to create an alternative option for gmail client, which the sole purpose is to reduce features and imrpove readability for the design.

## Progress of Development
---
Our development progress on this project may involve few tools that we were not familiar with or tools that we already know and are not good at.

First of all, as the gmail client is going to be a web-based interface, we're going to be needing a static file server, a WSGI server to handle request for endpoints, and a template engine, all that are done with a micro web framework called Flask

We are going to be using Flask to be doing those tasks which it has all of those requirements implemented with few main dependencies, like the Werkzeug library (which stands for "tool" in German) for WSGI server, the Jinja template engine, and a lot more.

Now we have the essentials for loading a web page through GET request, we can now implement the gmail dashboard for inbox, sent items, drafts, and the actions like compose.
For those things that are going to be done through the gmail backend, we might need a API wrapper for gmail, which is a library tool that allows us to make authenticated requests to google and retrieve metadata, modify, or make actions.
For those dependencies can be found in ../../requirements.txt file, so for the main ones we have the one for account authentication and google client library to build a service instance that can retrieve user data.
We can create a google console app which allows us to make request through, it has its own client id, it can also set specific scopes, test users, callback uri for the web server. So first of all, the user needs to grant access and they can allow scopes that are required to make the app function normally, after that, the response object is passed into the callback uri as url arguments, we can use those values to create a session and in that session we got the token and refresh token that is used when the token expires.
With the token, we can then request for the credentials that is passed in as a mapping to the build object to create a service instance, in this case is defined as gmail and "v1".

Now we can get into retrieving the message items under different labels, basically we can pass in the labels, user, or query to get a list of message, for each individual message we can use the id value to request for the full metadata for the message as a dictionary. Evenetually, we need a message body evaluation method for breaking it down and parsing it as html, so we can pass the subject, sender, recipient, date, and message body (either in the form of plain text or html), and put them in a custom defined object called `Message`, it can be used for having properties that can be accessed as an object, which is easier for the other to access.

For the dashboard design on the frontend, we decided to minimize the option lists to "inbox", "sent items", "drafts" to make it simpler, we also created the compose and make it easier to access.

One key design from us is that we used dropdown menu instead of a seperate page for the full message body, which is ideal because users don't have to nevigate to another page which can confuse people sometimes. This doesn't indicate that it's slower, since gmail kind of does the same thing by loading all the query data (which makes it more like a single page application) and it probabaly takes a lot of time for people with slow connection.

## Evidence and Reasoning

https://www.noisolation.com/global/research/why-do-many-seniors-have-trouble-using-technology/
9 percent of seniors at the age of 75 or over have severe visual impairments, and 18 percent have severe hearing limitations in the EU (Eurostat, 2017). Additionally, U.S statistics show that “23% of older adults indicate that they have a physical or health condition that makes reading difficult or challenging” (Pew Research Centre, 2014).
As many as 77 percent of seniors report that they would require assistance were they to try and learn how to use a smartphone or tablet. Additionally, of those who are already on the internet but do not use social networking sites, 56 percent say they would need help to connect with friends and family (Pew Research Centre, 2014).

https://www.theguardian.com/technology/askjack/2013/oct/10/email-internet-elderly-users
My father is 82 and has early-stage dementia that affects his short-term memory. He has a difficult time remembering instructions and tasks. Too much information, whether visual or verbal, confuses him. (In addition, his eyesight is not great, nor is his touch sensitivity.) I am looking for a bare-bones laptop that would allow him to send/receive email and look up information on the internet.