from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import UsuarioLector
from django.db import IntegrityError, transaction

# --------------------------
# Pruebas de Login y Registro
# --------------------------
class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='usuario#raro',
            password='P@ssw0rd!"#$%&/()=¿?*+~{.,<>|¬°^'
        )
        UsuarioLector.objects.create(usuario=self.user)
        self.login_url = reverse('LoginUsuario')
        self.home_url = reverse('Inicio')

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'usuario#raro',
            'password': 'P@ssw0rd!"#$%&/()=¿?*+~{.,<>|¬°^'
        })
        self.assertRedirects(response, self.home_url)

    def test_create_invalid_user(self):
        with self.assertRaises(ValidationError):
            try:
                user = User(
                    email='invalidemail',
                    password='test123'
                )
                user.full_clean()
                user.save()
            except ValidationError as e:
                print("Errores de validación:", e.message_dict)
                raise e

        self.assertFalse(User.objects.filter(email='invalidemail').exists())

    def test_create_user_with_existing_username(self):
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='test123'
        )

        with self.assertRaises(IntegrityError):
            try:
                with transaction.atomic():
                    User.objects.create_user(
                        username='existinguser',
                        email='test2@example.com',
                        password='test456'
                    )
            except IntegrityError as e:
                print("Error de integridad:", str(e))
                raise e

        # Verificar que solo existe un usuario con ese username
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)
    
    def test_create_users_with_same_email_different_username(self):
        test_email = "test@example.com"

        user1 = User.objects.create_user(
            username='usuario1',
            email=test_email,
            password='password123'
        )
        
        try:
            user2 = User.objects.create_user(
                username='usuario2',
                email=test_email,
                password='password456'
            )
            
            # Si se crea sin errores, verificar que existen ambos
            users = User.objects.filter(email=test_email)
            self.assertEqual(users.count(), 2)
            self.assertNotEqual(users[0].username, users[1].username)
            
        except IntegrityError:
            # Si falla por email único, verificar que solo existe el primero
            users = User.objects.filter(email=test_email)
            self.assertEqual(users.count(), 1)
            print("El sistema está configurado para emails únicos")