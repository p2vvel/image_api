Hi there! 

Thank you for interest in our Backend (Python + Django) Engineer position. We’re excited to get to know your technical skill better. See the task below. Fingers crossed and good luck!


Using Django REST Framework, write an API that allows any user to upload an image in PNG or JPG format.

You are allowed to use any libraries or base projects / cookie cutters you want (but using DRF is a hard requirement).

Skip the registration part, assume users are created via the admin panel.

Requirements:

* it should be possible to easily run the project. docker-compose is a plus
* users should be able to upload images via HTTP request
* users should be able to list their images
* there are three bultin account tiers: Basic, Premium and Enterprise:
* users that have "Basic" plan after uploading an image get: 
    * a link to a thumbnail that's 200px in height
* users that have "Premium" plan get:
    * a link to a thumbnail that's 200px in height
    * a link to a thumbnail that's 400px in height
    * a link to the originally uploaded image
* users that have "Enterprise" plan get
    * a link to a thumbnail that's 200px in height
    * a link to a thumbnail that's 400px in height
    * a link to the originally uploaded image
    * ability to fetch a link to the (binary) image that expires after a number of seconds (user can specify any number between 300 and 30000)
* apart from the builtin tiers, admins should be able to create arbitrary tiers with the following things configurable:
    * arbitrary thumbnail sizes
    * presence of the link to the originally uploaded file
    * ability to generate expiring links
* admin UI should be done via django-admin
* there should be no custom user UI (just browsable API from Django Rest Framework)
* remember about:
    * tests
    * validation
    * performance considerations (assume there can be a lot of images and the API is frequently accessed)


Please focus on code cleanliness and quality.

Submit your solution to bdd2022q2@hexocean.com within 10 days from receiving this message. Solutions sent after this date or to a different email won’t be taken into account. If you need more time, please let us know as soon as you can. The solution should include:

All source files,
A short README written in English that explains how to set up the project,
The time it took you to perform the task,

Bonus for:
* git repository
* live preview

Feel free to contact us if you have any questions!
