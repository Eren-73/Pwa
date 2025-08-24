from django.shortcuts import render, redirect, get_object_or_404
from .models import Devis, LigneDevis,Client
from .forms import DevisForm, LigneDevisForm,ClientForm
from django.forms import modelformset_factory
from django.urls import reverse
from .utils import generate_qr_code

def creer_devis(request):
    LigneDevisFormSet = modelformset_factory(
        LigneDevis, form=LigneDevisForm, extra=3, can_delete=True
    )

    if request.method == 'POST':
        devis_form = DevisForm(request.POST)
        formset = LigneDevisFormSet(request.POST, queryset=LigneDevis.objects.none())

        if devis_form.is_valid() and formset.is_valid():
            devis = devis_form.save()
            
            # Enregistrer chaque ligne de devis
            for form in formset:
                if form.cleaned_data:  # éviter les lignes vides
                    ligne = form.save(commit=False)
                    ligne.devis = devis
                    ligne.save()

            # ⚡ Utiliser l'IP locale de ton PC pour que le téléphone y accède
            current_site_ip = "192.168.1.68"
            devis_url = f"http://{current_site_ip}:8000{reverse('imprimer_devis', args=[devis.pk])}"
            print("URL générée pour QR:", devis_url)

            print(reverse('imprimer_devis', args=[13])) 

            # Générer et enregistrer le QR code
            print("Lien dans le QR :", devis_url)
            devis.qr_code.save(
                f"qr_{devis.pk}.png",
                generate_qr_code(devis.numero_devis),
                save=True
            )



            return redirect('imprimer_devis', pk=devis.pk)

    else:  # GET
        devis_form = DevisForm()
        formset = LigneDevisFormSet(queryset=LigneDevis.objects.none())

    return render(request, 'creer_devis.html', {
        'devis_form': devis_form,
        'formset': formset
    })

def imprimer_devis(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    lignes = devis.lignes.all()
    
    return render(request, 'devis_template.html', {
        'devis': devis,
        'lignes': lignes
    })

def dashboard(request):
    # Filtrer par date si des paramètres GET sont passés
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    devis_list = Devis.objects.all().order_by('-date_emission')

    if date_debut and date_fin:
        devis_list = devis_list.filter(
            date_emission__range=[date_debut, date_fin]
        )

    return render(request, 'dashboard.html', {'devis_list': devis_list})






def liste_clients(request):
    clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': clients})


def ajouter_client(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')

        Client.objects.create(
            nom=nom, prenom=prenom, email=email, telephone=telephone, adresse=adresse
        )
        return redirect('liste_clients')
