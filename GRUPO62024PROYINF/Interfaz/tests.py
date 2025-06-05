from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from .models import Empleado, TagBoletin, UsuarioLector

class LoginTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Datos compartidos para TODAS las pruebas
        cls.user = User.objects.create_user(username='lector1', password='P@ssw0rd123')
        cls.usuario_lector = UsuarioLector.objects.create(usuario=cls.user)
        cls.empleado_u3i = User.objects.create_user(username='u3i_user', password='u3i_pass')
        Empleado.objects.create(usuario=cls.empleado_u3i, tipo='equipo_u3i')
        cls.tag = TagBoletin.objects.create(nombre='Tecnología')
        cls.suscribir_url = reverse('suscribirTema', args=[cls.tag.nombre])
        cls.desuscribir_url = reverse('desuscribirTema', args=[cls.tag.nombre])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Limpieza de todos los objetos creados
        User.objects.all().delete()
        TagBoletin.objects.all().delete()

    def test_suscripcion_exitosa(self):
        self.client.login(username='lector1', password='P@ssw0rd123')
        response = self.client.post(self.suscribir_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.usuario_lector.preferenciasTags.exists())

    def test_desuscripcion_exitosa(self):
        self.usuario_lector.preferenciasTags.add(self.tag)
        self.client.login(username='lector1', password='P@ssw0rd123')
        response = self.client.post(self.desuscribir_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.usuario_lector.preferenciasTags.exists())

class UserCreationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.existing_user = User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='test123'
        )

    def test_create_user_with_existing_username(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username='existinguser',
                    email='test2@example.com',
                    password='test456'
                )
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

    def test_create_users_with_same_email_different_username(self):
        test_email = "test4@example.com"
        User.objects.create_user(username='usuario1', email=test_email, password='password123')
        
        User.objects.create_user(username='usuario2', email=test_email, password='password456')
        users = User.objects.filter(email=test_email)
        self.assertEqual(users.count(), 2)