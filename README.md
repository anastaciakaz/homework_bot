# homework_bot
This is a Telegram bot for keeping you updated about your homework status.
The bot accesses the Practicum.Homework service API and finds out the status of your homework: whether your homework was reviewed, whether it was checked, and if it was checked, then the reviewer accepted it or returned it for revision.
## Technology stack:
- Python 3.7
- Telegram Bot API
- pytest
## The functionality
Bot:
- queries the Practicum.Homework API once every 10 minutes and checks the status of the homework submitted for review;
- analyzes the API response and sends you a corresponding notification in Telegram when updating the status;
- logs its work and notifies about issues with a message in Telegram.

