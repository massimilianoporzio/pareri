"""Test per le funzionalità base del modello BaseModel e DummyModel.

Questo modulo contiene test per la creazione, aggiornamento e gestione
del modello fittizio DummyModel che eredita da BaseModel.
"""

# pylint: disable=unused-argument, no-member

import time
import uuid
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.db import connection, models
from django.test import TestCase

from server.common.models import BaseModel

# ----------------------------------------------------------------------
# 1. Modello Fittizio (DummyModel)
# ----------------------------------------------------------------------


# Deve ereditare da BaseModel
class DummyModel(BaseModel):
    """Un modello semplice per testare la funzionalità di BaseModel."""

    # Aggiungi un campo, anche se fittizio, per la validità del modello
    test_field = models.CharField(max_length=50, default='test')

    class Meta:
        """Meta informazioni per DummyModel."""

        # FONDAMENTALE: registra questo modello fittizio sotto l'app 'common'
        app_label = 'common'
        # Non è di produzione, non deve essere migrato (gestito da setUpClass)
        managed = False


# ----------------------------------------------------------------------
# 2. Classe di Test con Creazione Tabella Forzata
# ----------------------------------------------------------------------


# Usiamo una classe per sfruttare i metodi setUpClass e tearDownClass
@pytest.mark.django_db
class TestBaseModel(TestCase):
    """Test per le funzionalità base del modello BaseModel."""

    @classmethod
    def setUpClass(cls):
        """Crea la tabella del modello fittizio nel DB di test."""
        super().setUpClass()
        # Connessione allo schema editor per la creazione forzata della tabella
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(DummyModel)

    @classmethod
    def tearDownClass(cls):
        """Elimina esplicitamente la tabella del modello fittizio alla fine."""
        # Elimina la tabella per non lasciare artefatti nel DB di test
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(DummyModel)
        super().tearDownClass()

    # ------------------------------------------------------------------
    # 3. Funzioni di Test (La tua funzione originale)
    # ------------------------------------------------------------------

    def test_base_model_creation(self):
        """Test che un'istanza può essere creata e ha i valori di default."""
        # Questa riga ora dovrebbe funzionare senza ProgrammingError
        obj = DummyModel.objects.create()

        # Test per i campi della BaseModel
        assert isinstance(obj.id, uuid.UUID)
        assert obj.created_at is not None
        assert obj.updated_at is not None

        # Assumendo che BaseModel abbia un campo 'is_active'
        # assert obj.is_active is True

    # Nel file tests/test_common_base_model.py

    def test_base_model_update(self):
        """Testa l'aggiornamento del campo 'version' (timestamp/bigint)."""
        # 1. Creazione
        obj = DummyModel.objects.create(test_field='Initial')
        initial_version = obj.version
        # 2. Aggiungi un piccolo ritardo (importante per i timestamp)
        # Senza ritardo, obj.version potrebbe non cambiare perché il
        # codice è troppo veloce.

        time.sleep(0.001)  # Ritardo di 1 millisecondo
        time.sleep(0.001)  # Ritardo di 1 millisecondo

        # 3. Aggiornamento
        obj.test_field = 'Updated'
        obj.save()

        # 4. Asserzione Corretta: Il nuovo valore deve essere MAGGIORE
        #  del precedente
        assert obj.version > initial_version
        # Asserzione accessoria (opzionale)
        assert obj.updated_at > obj.created_at

    def test_save_sets_user_fields(self):
        """Test che i campi utente siano impostati correttamente."""
        user_model = get_user_model()
        user = user_model.objects.create(
            username='testuser', first_name='Test', last_name='User'
        )
        with patch('server.common.models.get_current_user', return_value=user):
            obj = DummyModel()
            obj.save()
            # Il campo created_by potrebbe non essere impostato
            #  a causa della logica Django
            # Verifica solo updated_by, che viene sempre impostato
            assert obj.updated_by == user
            assert obj.updated_by == user
            # Verifica solo updated_by_fullname
            assert obj.updated_by_fullname in {
                getattr(user, 'nome_utente', None),
                str(user),
            }

    def test_created_by_fields_on_first_save(self):
        """Test che i campi created_by siano impostati al primo salvataggio."""
        user_model = get_user_model()
        user = user_model.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
        )
        with patch('server.common.models.get_current_user', return_value=user):
            obj = DummyModel()
            obj.save()
            assert obj.created_by == user
            assert obj.created_by_fullname in {
                getattr(user, 'nome_utente', None),
                str(user),
            }

    def test_save_with_no_user(self):
        """Test che i campi utente restano None se non c'è utente corrente."""
        with patch('server.common.models.get_current_user', return_value=None):
            obj = DummyModel()
            obj.save()
            assert obj.created_by is None
            assert obj.updated_by is None

    def test_save_with_anonymous_user(self):
        """Test che i campi utente restano None se l'utente è anonimo."""

        class AnonymousUser:
            """Simula un utente anonimo."""

            is_anonymous = True

        with patch(
            'server.common.models.get_current_user',
            return_value=AnonymousUser(),
        ):
            obj = DummyModel()
            obj.save()
            assert obj.created_by is None
            assert obj.updated_by is None

    def test_save_with_created_by_already_set(self):
        """Test che created_by non venga sovrascritto se già impostato."""
        user_model = get_user_model()
        user1 = user_model.objects.create(
            username='user1',
            email='user1@aslcn1.it',
        )
        user2 = user_model.objects.create(
            username='user2',
            email='user2@aslcn1.it',
        )
        with patch('server.common.models.get_current_user', return_value=user2):
            obj = DummyModel(created_by=user1)
            obj.save()
            assert obj.created_by == user1
            assert obj.updated_by == user2
