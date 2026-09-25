from django.contrib.auth import get_user_model
User = get_user_model()

# Create user and save to the database
user = User.objects.create_user('Alice_SRS001', 'alicegabriela2102@gmail.com', 'DS2K24')

# Update fields and then save again
user.first_name = 'Alice'
user.last_name = 'Souza'
user.save()


