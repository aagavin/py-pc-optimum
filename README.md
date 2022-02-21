[![CodeFactor](https://www.codefactor.io/repository/github/aagavin/py-pc-optimum/badge)](https://www.codefactor.io/repository/github/aagavin/py-pc-optimum)


# pc-optimum-pdf mailer
Send pdf of the webpage https://www.pcoptimum.ca/offers to an email using your provided smpt provider


## Setup

* Set up virutal env:

  * `python3 -m venv venv`
  * `source venv/bin/activate`


* Set up environment variables:


  * `E_USERNAME` email server username
  * `E_PASSWORD` email server password (Should be application specific)
  * `E_FROM` email to use as the FROM feild in the email
  * `E_TO` email your sending the email to
  * `SMTP_PORT` email server port
  * `SMTP_SERVER` smtp server name

* Run with `python3 main.py <pcoptimum.ca username> <pcoptimum.ca password>`
