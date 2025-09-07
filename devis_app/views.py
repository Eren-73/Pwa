from django.shortcuts import render, redirect, get_object_or_404
from .models import Devis, LigneDevis,Client,Categorie,Produit
from .forms import DevisForm, LigneDevisForm,ClientForm,ProduitForm,CategorieForm
from django.forms import modelformset_factory
from django.urls import reverse
from .utils import generate_qr_code
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
# from docx import Document
# from django.http import HttpResponse

# import weasyprint
# import openpyxl
# import json


def creer_devis(request):
    LigneDevisFormSet = modelformset_factory(
        LigneDevis, form=LigneDevisForm, extra=0, can_delete=True
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
            devis_url = f"http://{current_site_ip}:8000{reverse('devis_template', args=[devis.pk])}"


            # Générer et enregistrer le QR code
            print("Lien dans le QR :", devis_url)
            devis.qr_code.save(
                f"qr_{devis.slug}.png",
                generate_qr_code(devis.numero_devis),
                save=True
            )



            return redirect('devis_template', slug=devis.slug)

    else:  # GET
        devis_form = DevisForm()
        formset = LigneDevisFormSet(queryset=LigneDevis.objects.none())

    return render(request, 'creer_devis.html', {
        'devis_form': devis_form,
        'formset': formset
    })

def devis_template (request, slug):
    devis = get_object_or_404(Devis, slug=slug)
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
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()  # ✅ slug généré automatiquement
            return redirect('liste_clients')
    else:
        form = ClientForm()
    return render(request, 'ajouter_client.html', {'form': form})

def modifier_client(request, slug):
    client = get_object_or_404(Client, slug=slug)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('liste_clients')
    else:
        form = ClientForm(instance=client)
    return render(request, 'modifier_client.html', {'form': form, 'client': client})


def supprimer_client(request, slug):
    client = get_object_or_404(Client, slug=slug)
    if request.method == 'POST':
        client.delete()
        return redirect('/clients/?deleted=1')
    return render(request, 'supprimer_client.html', {'client': client})

def devis_par_client(request, slug):
    client = get_object_or_404(Client, slug=slug)
    devis_list = Devis.objects.filter(client=client)
    return render(request, 'devis_par_client.html', {
        'client': client,
        'devis_list': devis_list
    })

def detail_devis(request, slug):
    devis = get_object_or_404(Devis, slug=slug)
    lignes = devis.lignes.all()
    return render(request, "devis_template.html", {
        "devis": devis,
        "lignes": lignes
    })

@csrf_exempt
def supprimer_devis_selectionnes(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            devis_ids = [int(i) for i in data.get("devis_ids", [])]  # conversion en int
            Devis.objects.filter(id__in=devis_ids).delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "Méthode non autorisée"}, status=405)


def liste_materiels(request):
    categories = Categorie.objects.prefetch_related('produit_set').all()
    return render(request, 'liste_materiels.html', {'categories': categories})

@csrf_exempt
def supprimer_produit(request, produit_id):
    if request.method == "POST":
        try:
            produit = Produit.objects.get(id=produit_id)
            produit.delete()
            return JsonResponse({"success": True})
        except Produit.DoesNotExist:
            return JsonResponse({"success": False, "error": "Produit introuvable"})
    return JsonResponse({"success": False, "error": "Méthode non autorisée"})

def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('liste_materiels')  # redirige vers la liste des matériels
    else:
        form = ProduitForm(instance=produit)

    return render(request, 'modifier_produit.html', {'form': form, 'produit': produit})



def ajouter_categorie(request):
    if request.method == "POST":
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_materiels')
    else:
        form = CategorieForm()
    return render(request, 'ajouter_categorie.html', {'form': form})

def ajouter_produit(request):
    if request.method == "POST":
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_materiels')
    else:
        form = ProduitForm()
    return render(request, 'ajouter_produit.html', {'form': form})



# def export_devis_word(request, slug):
#     devis = get_object_or_404(Devis, slug=slug)
#     doc = Document()
#     doc.add_heading(f'Devis {devis.numero_devis}', 0)
#     doc.add_paragraph(f'Client: {devis.client.nom} {devis.client.prenom}')
#     doc.add_paragraph(f'Date: {devis.date_emission}')
#     # ajouter les lignes de produits etc.
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
#     response['Content-Disposition'] = f'attachment; filename=Devis_{devis.numero_devis}.docx'
#     doc.save(response)
#     return response


# def export_devis_word(request, slug):
#     devis = get_object_or_404(Devis, slug=slug)
#     doc = Document()
#     doc.add_heading(f'Devis {devis.numero_devis}', 0)
#     doc.add_paragraph(f'Client: {devis.client.nom} {devis.client.prenom}')
#     doc.add_paragraph(f'Date: {devis.date_emission}')
#     # ajouter les lignes de produits etc.
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
#     response['Content-Disposition'] = f'attachment; filename=Devis_{devis.numero_devis}.docx'
#     doc.save(response)
#     return response



def export_devis_excel(request, slug):
    devis = get_object_or_404(Devis, slug=slug)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Devis"
    ws.append(["Produit", "Qté", "Unité", "Prix Unitaire", "Remise", "P.U Net", "Total TTC"])
    for ligne in devis.lignes.all():
        ws.append([ligne.produit.nom, ligne.quantite, ligne.unite, ligne.pu, ligne.remise, ligne.pu_net, ligne.total_ttc])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Devis_{devis.numero_devis}.xlsx'
    wb.save(response)
    return response