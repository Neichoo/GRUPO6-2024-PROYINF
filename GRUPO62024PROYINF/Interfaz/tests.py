from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from .models import Empleado, TagBoletin, UsuarioLector

class LoginTestCase(TestCase):
    def setUp(self):
        # Crear usuario lector
        self.user = User.objects.create_user(
            username='lector1',
            password='P@ssw0rd123'
        )
        self.usuario_lector = UsuarioLector.objects.create(usuario=self.user)
        
        # Crear empleado u3i (si es necesario para otras pruebas)
        self.empleado_u3i = User.objects.create_user(username='u3i_user', password='u3i_pass')
        Empleado.objects.create(usuario=self.empleado_u3i, tipo='equipo_u3i')
        
        # Crear tag sin campo 'empleado'
        self.tag = TagBoletin.objects.create(nombre='Tecnología')
        
        # URLs
        self.suscribir_url = reverse('suscribirTema', args=[self.tag.nombre])
        self.desuscribir_url = reverse('desuscribirTema', args=[self.tag.nombre])

    def test_suscripcion_exitosa(self):
        self.client.login(username='lector1', password='P@ssw0rd123')
        response = self.client.post(self.suscribir_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.usuario_lector.preferenciasTags.filter(nombre='Tecnología').exists())

    def test_desuscripcion_exitosa(self):
        self.usuario_lector.preferenciasTags.add(self.tag)
        self.client.login(username='lector1', password='P@ssw0rd123')
        response = self.client.post(self.desuscribir_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.usuario_lector.preferenciasTags.exists())

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