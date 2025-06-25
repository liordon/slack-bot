# Design

The system is comprised of the following components:

## flask app

the application wrapper that listens to webhooks and passes them into the system.

## bot_policy

receives the user messages from the app and processes them. the main functions here are `classify_and_respond` for
handling new classification requests and `handle_message` for handling in-thread responses and fixes to existing
classification attempts. This module uses a `Classifier` to process the input requests, a `SecurityEstimator` to
estimate security risks and an `Attitude` to formulate responses.

## Classifier

Formulates a request object out of the user's input. The ini tial Idea was to use an LLM for this, but the dependency
management for LLM is such a hassle that I kept postponing it indefinitely. I ended up with a _good enough_ regex based
parser. It does exactly what you would expect, using key phrases.

## SecirutyEstimator

since there was very little correlation in the db between the request details, existing fields and security risk score,
this part seemed to be pretty undefined. I ended up just guesstimating based on the fields of each request, looking for
indications of risk based on my own priors --- which is not very good.

## Attitude

The attitude customizes the bot's responses to the user. you can think about it as a 'skin' to the conversational user
interface. I implemented two different attitudes just to demonstrate the mechanism, one professional and one
horrifically unprofessional. The bot policy dictates what kind of message needs to be conveyed to the user, and the
attitude implementation is in charge of formulating the response.