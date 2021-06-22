#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime

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
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venue_data = []

    result = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    venues = Venue.query.all()

    for city in result:
        if venues.city == city.city and venues.state == city.state:
            shows = Show.query.filter(Show.venue_id == venues.id).all()
            venue_data.append({
                'id': venues.id,
                'name': venues.name,
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
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    data = []

    search_term = request.form.get('search_term', '')
    result = Venue.query.filter_by(
    Venue.name.ilike('%' + search_term +'%')).all()
    
    shows = Show.query.filter(Show.venue_id == result.id).all()

    for venue in result:
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
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
  data= []
  venues = Venue.query.get(venue_id)
  shows = Show.query.filter(Show.venue_id == venues.id).all()
  past_shows = past_shows(shows)
  upcoming_shows = upcoming_shows(shows)

  data.append({
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
          "past_shows": past_shows,
          "upcoming_shows": upcoming_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows_count": len(upcoming_shows),
        })

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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error= False

    try:
        venue = Venue(name=request.form['name'],
                      city=request.form['city'],
                      state=request.form['state'],
                      address=request.form['address'],
                      phone=request.form['phone'],
                      genres=request.form.getlist('genres'),
                      image_link=request.form['image_link'],
                      facebook_link=request.form['facebook_link'],
                      website_link=request.form['website_link'],
                      seeking_talent=True if 'seeking_talent' in request.form else False,
                      seeking_description=request.form['seeking_description']
                      )

        db.session.add(venue)
        db.session.commit()

    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        error= True
        db.session.rollback()
        
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
   # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue was successfully deleted!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be deleted.')

    finally:
        db.session.close()

    return render_template('pages/home.html')


#----------------------------------------------------------------------------#
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    result = Artist.query.all()

    for artist in result:
        data.append = [{
            "id": artist.id,
            "name": artist.name
        }]

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    data = []
    search_term = request.form.get('search_term', '')
    result = Artist.query.filter_by(
        Artist.name.ilike("%{}%".format(search_term))).all()
    for artist in result:
        data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": 0,
            }
        )
    response = {
        "count": (len(data)),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
  data= []

  artists = Venue.query.get(artist_id)
  shows = Show.query.filter(Show.artist_id == artists.id).all()

  past_shows = past_shows(shows)
  upcoming_shows = upcoming_shows(shows)

  data.append({
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
          "past_shows": past_shows,
          "upcoming_shows": upcoming_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows_count": len(upcoming_shows),
        })

  return render_template('pages/show_artist.html', artist=data)


#----------------------------------------------------------------------------#
#  Update
#  --------------------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    result = db.session.query(Artist).filter(Artist.id == artist_id).first()
    form = ArtistForm(obj=result)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=result)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    try:
        artist.name = request.form['name'],
        artist.city = request.form['city'],
        artist.state = request.form['state'],
        artist.phone = request.form['phone'],
        artist.genres = request.form.getlist('genres'),
        artist.facebook_link = request.form['facebook_link'],
        artist.image_link = request.form['image_link'],
        artist.website_link = request.form['website_link'],
        artist.seeking_venue = True if 'seeking_venue' in request.form else False,
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()

    except:
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    result = db.session.query(Venue).filter(Venue.id == venue_id).first()
    form = VenueForm(obj=result)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=result)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    try:
        venue.name = request.form['name'],
        venue.city = request.form['city'],
        venue.state = request.form['state'],
        venue.address = request.form['address'],
        venue.phone = request.form['phone'],
        venue.genres = request.form.getlist('genres'),
        venue.image_link = request.form['image_link'],
        venue.facebook_link = request.form['facebook_link'],
        venue.website_link = request.form['website_link'],
        venue.seeking_talent = True if 'seeking_talent' in request.form else False,
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()

    except:
        db.session.rollback()

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
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error= False
    try:
        artist = Artist(name=request.form['name'],
                        city=request.form['city'],
                        state=request.form['state'],
                        phone=request.form['phone'],
                        genres=request.form.getlist('genres'),
                        facebook_link=request.form['facebook_link'],
                        image_link=request.form['image_link'],
                        website_link=request.form['website_link'],
                        seeking_venue=True if 'seeking_venue' in request.form else False,
                        seeking_description=request.form['seeking_description']
                        )
        db.session.add(artist)
        db.session.commit()

    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        error=True
        db.session.rollback()
       
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []

    result = Show.query.join(
        Venue, (Venue.id == Show.venue_id)
    ).join(
        Artist, (Artist.id == Show.artist_id)
    ).all()

    for shows in result:
        data.append(
            {
                "venue_id": shows.venue_id,
                "venue_name": shows.venue.name,
                "artist_id": shows.artist_id,
                "artist_name": shows.artist.name,
                "artist_image_link": shows.artist.image_link,
                "start_time": shows.start_time
            }
        )

    
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error= False
    try:
        show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()


    except:
        error=True
        db.session.rollback()

    finally:
        db.session.close()
    
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')


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
