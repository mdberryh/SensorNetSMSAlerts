# SensorNetSMSAlerts
Using the sensor net api will check stove temps and send SMS alerts when an issue arises.


The code loops foreever (sleeping for 5 minutes), checks sensor data and determines if an alert needs to be sent. If an alert needs to be sent, it will check an in memory array of sent SMS logs and see if it has already sent a message during the throttle limit.

The sms.secrets are the credentials from Twilio

The sms.conf file holds phone numbers to send text messages to and from. Note that the from number must be one associated with your Twillio account. In this case it would have been better to store the Twillio phone number in sms.secrets file.

The docker container will run the python script and fetch the dependencies.

To build the docker container...
cd to the location of the code/dockerfile.
type "docker build -t python-sensor-alerts ."

To run the container it is best to run interactively and keep an eye for errors. 
"docker run -it --rm python-sensor-alerts"

If there are no errors you can run the container as a deamon...
"docker run -d --rm python-sensor-alerts"

# warning
Please note that you are programatically sending SMS messages. Twillio can be set to charge your card when your balance is low. It is possible that if your program gets stuck in a bad loop it could deplete your $ in twilio and constantly charge your card to refil.

Also, it seems that twillio charges $1/mo for having a phone number and US SMS messsages are $0.0075 at the time of writing this.
