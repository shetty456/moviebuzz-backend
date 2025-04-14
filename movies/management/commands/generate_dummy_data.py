from reservations.models import Seat,Showtime,Auditorium,Review,BookingHistory
from movies.models import Language,Genre,Movie,MovieGenre
from user.models import UserAccount
from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
import random
from faker import Faker


fake = Faker()


class Command(BaseCommand):

    def handle(self,*args, **kwargs):

        #create lanugages
        language = [Language.objects.create(name=fake.language_name()) for _ in range(5)]

        #create geners
        genres = [Genre.objects.create(name=fake.word()) for _ in range(5)]

        #create users
        User = []

        for _ in range(20):
            user = UserAccount.objects.create_user(
                name = fake.name(),
                email = fake.unique.email(),
                password = "Password@123",
                role = random.choice(['admin','user'])
            )
            User.append(user)

        #create Movies
        movies = []

        for _ in range(20):
            movie = Movie.objects.create(
                title = fake.sentence(nb_words=3),
                description = fake.text(),
                language_id = random.choice(language),
                duration=timedelta(minutes=random.randint(90, 180)),
                user_id = random.choice(User),
                rate=random.uniform(1.0, 5.0),
                price=random.uniform(100.0, 500.0),
                image_url= fake.image_url()

            )    
            #attach gener to movie genere
            for genre in random.sample(genres,2):
                MovieGenre.objects.create(movie=movie,genre=genre)

            movies.append(movie)    

        #create auditorium
        auditorium = []
        for _ in range(5):    
            auditoriums = Auditorium.objects.create(
                name = fake.company(),
                total_seats = random.randint(50, 150),
                movie = random.choice(movies),
                total_shows = str(random.randint(3, 8)),
                place = fake.city()
            )
            auditorium.append(auditoriums)
         # Create Showtimes
        showtimes = []
        for _ in range(20):
            showtime = Showtime.objects.create(
                movie_id=random.choice(movies),
                auditorium_id=random.choice(auditorium),
                status=random.choice(['scheduled', 'cancelled', 'completed']),
                start_time=fake.date_time_between(start_date="-1d", end_date="+5d", tzinfo=timezone.utc)
            )
            showtimes.append(showtime)

            # Create Seats for the showtime
            for seat_num in range(1, 11):  # 10 seats per show
                Seat.objects.create(
                    showtime_id=showtime,
                    seat_number=f"{chr(65 + seat_num // 10)}{seat_num}",
                    is_booked=random.choice([True, False])
                )

        # Create Reviews
        for _ in range(10):
            Review.objects.create(
                user_id=random.choice(User),
                movie_id=random.choice(movies),
                rating=random.randint(1, 5),
                comment=fake.sentence()
            )

        # Create Booking History
        for _ in range(10):
            BookingHistory.objects.create(
                user_id=random.choice(User),
                movie_id=random.choice(movies),
                showtime_id=random.choice(showtimes),
                tickets=random.randint(1, 5)
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))

        
