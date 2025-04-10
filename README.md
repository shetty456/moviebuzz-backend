# MovieBuzz Backend 

This project is a web-based application for booking movie tickets. It allows users to view available movies, check showtimes, and book tickets. This app is built using Python and Django,DRF, with a simple, user-friendly interface.

## table of contents
-[installation]
-[usage]
-[setup]
-[testing]
-[featuers]

# Set up a virtual environment (optional but recommended)

`python3 -m venv venv`
`source venv/bin/activate  # On macOS/Linux`
`venv\Scripts\activate  # On Windows`

  
  

## Installation

To get started, clone the repository and install the necessary dependencies using `requirements.txt`.

## clone repository

`git clone https://github.com/shetty456/moviebuzz-backend.git`
`cd moviebuzz-backend`

## Install dependencies
`pip install -r requirements.txt`

## migrate database
`python manage.py makemigrations`
`python manage.py migrate`

## create superuser
`python manage.py createsuperuser`

## run server
`python manage.py runserver`

## features

User Registration & Login: Users can sign up, log in, and manage their accounts.
Movie Listings: View available movies, showtimes, and booking details.
Ticket Booking: Book tickets for available movie showtimes.
Admin Panel: Admin can manage movies, showtimes, and user bookings.





