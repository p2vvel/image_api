# Image API
Simple REST API built in Python with Django and DRF.

Gives ability to upload images, that later can be downloaded as:
* original files
* resized thumbnails
* can be converted to binary images (black/white) and served as binary data for specified time

Possibilities are depending on users tier, there are some built-in tiers. Admins can also create new tiers and specify ability to download binary/original files or choose custom thumbnail sizes.

 I decided to make API available only for logged-in users and make uploaded photos available only for their owners (used X-SendFile for that). Structure of media links is also hidden behind randomly generated UUIDs. Thumbnails are generated on the upload (for performance - nginx could manage file serving).

 Used containers:
 * python (running API with gunicorn)
 * nginx (proxy server, serving images and static files)
 * postgres (DB)
 * redis (caching - I decided to use caching with TTL to generate expiring links to binary images)


### Coding time

Creating the thing took me about 2 days(didn't count how much exactly, but I assume that it was about 15-20 hours), most of the time was consumed by coding and trying new things (3/4 of the time I would say). Rest of the time was spent on writing tests, configuring docker and nginx.

## Start things up
Project can be started using `docker-compose up` in main folder. There's ready `.env` file with some default data. Passwords and login data should probably be changed, but I left them to make starting project easier. Project starts at `port 80`, but It can be changed in `docker-compose.yaml` file. Admin panel is available at `/admin`, it's the easiest way to log-in using default credentials. Informations necessary to log in to admin panel (and to the browsable API in the browser) are `SUPERUSER_NAME` and `SUPERUSER_PASSWORD` from `.env` file.