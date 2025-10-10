from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from .models import Devis, ActionCommercial

# 🔹 Créer automatiquement un Profile quand un User est créé
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 🔹 Sauvegarder le Profile à chaque sauvegarde de User
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



# 🔹 Quand un devis est créé
@receiver(post_save, sender=Devis)
def track_devis_creation(sender, instance, created, **kwargs):
    if created and instance.utilisateur:
        ActionCommercial.objects.create(
            user=instance.utilisateur,
            action=f"Création du devis {instance.numero_devis}"
        )

# 🔹 Quand un utilisateur se connecte
@receiver(user_logged_in)
def track_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    ActionCommercial.objects.create(
        user=user,
        action="Connexion à l'application",
        ip_address=ip
    )

# 🔹 Quand un utilisateur se déconnecte
@receiver(user_logged_out)
def track_logout(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    ActionCommercial.objects.create(
        user=user,
        action="Déconnexion de l'application",
        ip_address=ip
    )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f"✅ {user.username} s'est connecté à {timezone.now()} depuis {request.META.get('REMOTE_ADDR')}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    print(f"🚪 {user.username} s'est déconnecté à {timezone.now()}")