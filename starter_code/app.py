#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request, Response,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import (
    Formatter, FileHandler, error
)
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# up coming shows & past shows
#----------------------------------------------------------------------------#


def upcoming_shows(shows):

    upcoming_shows = []
    currunt_time = datetime.now()

    for show in shows:
        if show.start_time > currunt_time:

            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    return upcoming_shows


def past_shows(shows):

    past_shows = []
    currunt_time = datetime.now()

    for show in shows:
        if show.start_time < currunt_time:

            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    return past_shows

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():

    data = []

    result = db.session.query(Venue.city, Venue.state).distinct(
        Venue.city, Venue.state)

    for city in result:
        venue_data = []
        venues = Venue.query.filter(Venue.state == city.state).filter(
            Venue.city == city.city).all()

        for venue in venues:

            shows = db.session.query(Show).filter(
                Show.venue_id == venue.id).all()

            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(upcoming_shows(shows))
            })
        data.append({
            'city': city.city,
            'state': city.state,
            'venues': venue_data
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    data = []

    search_term = request.form.get('search_term', '')
    result = Venue.query.filter(
        Venue.name.ilike('%' + search_term + '%')).all()

    for venue in result:

        shows = db.session.query(Show).filter(Show.venue_id == venue.id).all()

        data.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows(shows)),
            }
        )

    response = {

        "count": len(data),
        "data": data

    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    data = []
    venues = Venue.query.get(venue_id)
    shows = db.session.query(Show).filter(Show.venue_id == venues.id).all()
    past = past_shows(shows)
    upcoming = upcoming_shows(shows)

    data = {
        "id": venues.id,
        "name": venues.name,
        "genres": venues.genres,
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "image_link": venues.image_link,
        "facebook_link": venues.facebook_link,
        "website_link": venues.website_link,
        "seeking_talent": True if venues.seeking_talent in (True, 't', 'True') else False,
        "seeking_description": venues.seeking_description,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }

    return render_template('pages/show_venue.html', venue=data)

#----------------------------------------------------------------------------#
#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)
    try:
        venue = Venue(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      address=form.address.data,
                      phone=form.phone.data,
                      genres=form.genres.data,
                      image_link=form.image_link.data,
                      facebook_link=form.facebook_link.data,
                      website_link=form.website_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data
                      )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was successfully listed!')

    except:

        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')

    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue was successfully deleted!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be deleted.')
        print(sys.exc_info())

    finally:
        db.session.close()

    return render_template('pages/home.html')


#----------------------------------------------------------------------------#
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():

    data = []
    result = Artist.query.all()

    for artist in result:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    data = []
    search_term = request.form.get('search_term', '')
    result = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()

    for artist in result:

        shows = db.session.query(Show).filter(Show.venue_id == artist.id).all()

        data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(upcoming_shows(shows)),
            }
        )
    response = {
        "count": (len(data)),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    data = []

    artists = Artist.query.get(artist_id)
    shows = db.session.query(Show).filter(Show.artist_id == artists.id).all()
    past = past_shows(shows)
    upcoming = upcoming_shows(shows)

    data = {
        "id": artists.id,
        "name": artists.name,
        "genres": artists.genres,
        "city": artists.city,
        "state": artists.state,
        "phone": artists.phone,
        "website_link": artists.website_link,
        "facebook_link": artists.facebook_link,
        "seeking_venue": True if artists.seeking_venue in (True, 't', 'True') else False,
        "seeking_description": artists.seeking_description,
        "image_link": artists.image_link,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }

    return render_template('pages/show_artist.html', artist=data)


#----------------------------------------------------------------------------#
#  Update
#  --------------------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    result = db.session.query(Artist).filter(Artist.id == artist_id).first()
    form = ArtistForm(obj=result)

    return render_template('forms/edit_artist.html', form=form, artist=result)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    try:
        artist = Artist.query.get(artist_id)
        form = ArtistForm(request.form)
        form.populate_obj(artist)
        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    result = db.session.query(Venue).filter(Venue.id == venue_id).first()
    form = VenueForm(obj=result)

    return render_template('forms/edit_venue.html', form=form, venue=result)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    try:

        venues = Venue.query.get(venue_id)
        form = VenueForm(request.form)
        form.populate_obj(venues)
        db.session.commit()

    except:

        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form = ArtistForm(request.form)
    try:
        artist = Artist(name=form.name.data,
                        city=form.city.data,
                        state=form.state.data,
                        phone=form.phone.data,
                        genres=form.genres.data,
                        image_link=form.image_link.data,
                        facebook_link=form.facebook_link.data,
                        website_link=form.website_link.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data
                        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())

    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

    data = []

     # num_shows should be aggregated based on number of upcoming shows per venue.

    result = db.session.query(Show).filter(
        Show.start_time > datetime.now()).all()

    # flash(result)

    for shows in result:
        data.append({
            "venue_id": shows.venue_id,
            "venue_name": shows.venue.name,
            "artist_id": shows.artist_id,
            "artist_name": shows.artist.name,
            "artist_image_link": shows.artist.image_link,
            "start_time": str(shows.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    form = ShowForm(request.form)

    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )

        db.session.add(show)
        db.session.commit()
        flash('Success!')

    except:
        db.session.rollback()
        flash('Fail, Try Again')

    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
