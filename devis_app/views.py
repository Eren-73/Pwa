from django.shortcuts import render, redirect, get_object_or_404
from .models import Devis, LigneDevis,Client,Categorie,Produit,PointVente
from .forms import DevisForm, LigneDevisForm,ClientForm,ProduitForm,CategorieForm
from django.forms import modelformset_factory
from django.urls import reverse
from .utils import generate_qr_code
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from docx import Document
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required  # 🔹 AJOUT
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test
from .models import Devis, Profile
import weasyprint
import openpyxl
import json
from datetime import datetime
from django.conf import settings
from .forms import CommercialCreateForm
from .models import ActionCommercial
import os
from docx.oxml import parse_xml
import io

@login_required(login_url='login')
def creer_devis(request):
    LigneDevisFormSet = modelformset_factory(
        LigneDevis, form=LigneDevisForm, extra=0, can_delete=True
    )

    if request.method == 'POST':
        devis_form = DevisForm(request.POST)
        formset = LigneDevisFormSet(request.POST, queryset=LigneDevis.objects.none())

        if devis_form.is_valid() and formset.is_valid():
            devis = devis_form.save(commit=False)

            # 🔹 Lier le devis à l'utilisateur connecté (commercial)
            devis.utilisateur = request.user

            # ✅ Vérifier si TVA doit être appliquée
            apply_tva = request.POST.get("apply_tva", "yes")
            if apply_tva == "no":
                devis.appliquer_tva = False
            else:
                devis.appliquer_tva = True

            devis.save()

            # ✅ Enregistrer chaque ligne
            for form in formset:
                if form.cleaned_data:
                    ligne = form.save(commit=False)
                    ligne.devis = devis
                    ligne.save()

            # ✅ Générer le lien public
            current_site_ip = "192.168.1.68"
            devis_url = f"http://{current_site_ip}:8000{reverse('devis_template', args=[devis.pk])}"

            # ✅ Générer le QR code
            print("Lien dans le QR :", devis_url)
            devis.qr_code.save(
                f"qr_{devis.slug}.png",
                generate_qr_code(devis.numero_devis),
                save=True
            )

            return redirect('devis_template', slug=devis.slug)

    else:
        devis_form = DevisForm()
        formset = LigneDevisFormSet(queryset=LigneDevis.objects.none())

    # 🔹 Nombre total de devis créés par l’utilisateur connecté
    nombre_devis = Devis.objects.filter(utilisateur=request.user).count()

    return render(request, 'devis/creer_devis.html', {
        'devis_form': devis_form,
        'formset': formset,
        'nombre_devis': nombre_devis,  # ➕ tu peux l'afficher dans ton template
    })

def devis_template(request, slug):
    devis = get_object_or_404(Devis, slug=slug)
    lignes = devis.lignes.all()

    return render(request, 'devis/devis_template.html', {
        'devis': devis,
        'lignes': lignes,
        'qr_code_url': request.build_absolute_uri(devis.qr_code.url) if devis.qr_code else None,
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
    return render(request, 'clients/clients.html', {'clients': clients})


def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()  # ✅ slug généré automatiquement
            return redirect('liste_clients')
    else:
        form = ClientForm()
        return render(request, 'clients/ajouter_client.html', {'form': form})

def modifier_client(request, slug):
    client = get_object_or_404(Client, slug=slug)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('liste_clients')
    else:
        form = ClientForm(instance=client)
        return render(request, 'clients/modifier_client.html', {'form': form, 'client': client})


def supprimer_client(request, slug):
    client = get_object_or_404(Client, slug=slug)
    if request.method == 'POST':
        client.delete()
        return redirect('/clients/?deleted=1')
    return render(request, 'supprimer_client.html', {'client': client})

def devis_par_client(request, slug):
    client = get_object_or_404(Client, slug=slug)
    devis_list = Devis.objects.filter(client=client)
    return render(request, 'clients/devis_par_client.html', {
        'client': client,
        'devis_list': devis_list
    })

def detail_devis(request, slug):
    devis = get_object_or_404(Devis, slug=slug)
    # Récupère les lignes associées au devis pour l'affichage
    lignes = devis.lignes.all()

    return render(request, "devis/devis_template.html", {
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



def export_devis_excel(request, slug):
    devis = get_object_or_404(Devis, slug=slug)
    lignes = devis.lignes.all()

    # Create workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Devis {devis.numero_devis}"

    # Styles
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill, NamedStyle
    from openpyxl.styles.numbers import FORMAT_NUMBER_COMMA_SEPARATED1

    # Fonts
    title_font = Font(name='Arial', bold=True, size=14)
    header_font = Font(name='Arial', bold=True, size=11)
    normal_font = Font(name='Arial', size=10)
    bold = Font(name='Arial', bold=True, size=10)

    # Alignments
    right_align = Alignment(horizontal='right', vertical='center')
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')

    # Borders
    thin = Side(border_style='thin', color='000000')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    top_border = Border(top=thin)

    # Fill colors
    light_gray = 'E6E6E6'
    lighter_gray = 'F2F2F2'

    # Money format
    money_format = '#,##0.00 "XOF"'

    # Column widths optimized for content
    widths = {
        'A': 45,  # Designation
        'B': 8,   # Qté
        'C': 8,   # Unité
        'D': 15,  # Prix unitaire
        'E': 10,  # Remise
        'F': 15,  # P.U Net
        'G': 15,  # Total
    }
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # Row heights
    ws.row_dimensions[1].height = 30  # Logo row
    for row in range(2, 30):  # Adjust other rows
        ws.row_dimensions[row].height = 20

    # Insert logo if available
    try:
        logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'images', 'logo.png')
        if os.path.exists(logo_path):
            img = openpyxl.drawing.image.Image(logo_path)
            img.width = 200
            img.height = 90
            ws.add_image(img, 'A1')
    except Exception:
        pass

    # Header texts
    ws['D1'] = 'PROPOSITION COMMERCIALE'
    ws['D2'] = 'PROFORMA'
    for cell in ['D1', 'D2']:
        ws[cell].font = title_font
        ws[cell].alignment = right_align

    # Devis meta with styling
    ws['A4'] = f'Devis N° {devis.numero_devis}'
    ws['A5'] = f'Date: {devis.date_emission.strftime("%d/%m/%Y")}'
    for cell in ['A4', 'A5']:
        ws[cell].font = bold
        ws[cell].border = top_border

    # Client block with consistent styling
    row = 7
    ws[f'A{row}'] = 'CLIENT'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = PatternFill(start_color=light_gray, end_color=light_gray, fill_type='solid')
    row += 1

    client_data = [
        ('Nom', f"{devis.client.nom} {devis.client.prenom}"),
        ('Email', devis.client.email),
        ('Adresse', devis.client.adresse or ''),
    ]
    for label, value in client_data:
        ws[f'A{row}'] = label
        ws[f'B{row}'] = value
        ws[f'A{row}'].font = bold
        ws[f'B{row}'].font = normal_font
        ws[f'A{row}'].alignment = left_align
        ws[f'B{row}'].alignment = left_align
        row += 1

    # Commercial block with matching style
    crow = 7
    ws[f'D{crow}'] = 'CONSEILLER COMMERCIAL'
    ws[f'D{crow}'].font = header_font
    ws[f'D{crow}'].fill = PatternFill(start_color=light_gray, end_color=light_gray, fill_type='solid')
    crow += 1

    if devis.utilisateur:
        commercial_data = [
            ('Nom', f"{devis.utilisateur.first_name} {devis.utilisateur.last_name}"),
            ('Email', devis.utilisateur.email),
            ('Point de vente', devis.point_vente.nom if devis.point_vente else 'Non assigné'),
        ]
        for label, value in commercial_data:
            ws[f'D{crow}'] = label
            ws[f'E{crow}'] = value
            ws[f'D{crow}'].font = bold
            ws[f'E{crow}'].font = normal_font
            ws[f'D{crow}'].alignment = left_align
            ws[f'E{crow}'].alignment = left_align
            crow += 1
    else:
        ws[f'D{crow}'] = 'Commercial non assigné'
        ws[f'D{crow}'].font = normal_font

    # Products table with enhanced styling
    table_row = 12
    headers = ['Désignation', 'Qté', 'Unité', 'Prix unitaire', 'Remise', 'P.U Net', 'Total']
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=table_row, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = PatternFill(start_color=light_gray, end_color=light_gray, fill_type='solid')
        cell.alignment = center_align
        cell.border = border

    # Format product rows with proper number formatting
    for ligne in lignes:
        table_row += 1
        # Row data with proper types
        values = [
            (ligne.produit.nom, 'text', left_align),
            (ligne.quantite, 'number', right_align),
            (ligne.unite, 'text', center_align),
            (ligne.pu, 'money', right_align),
            (f"{ligne.remise}%", 'text', right_align),
            (ligne.pu_net, 'money', right_align),
            (ligne.total_ttc, 'money', right_align),
        ]
        
        for col_idx, (val, type_, align) in enumerate(values, 1):
            cell = ws.cell(row=table_row, column=col_idx, value=val)
            cell.font = normal_font
            cell.alignment = align
            cell.border = border
            
            if type_ == 'money':
                cell.number_format = money_format

    # Totals area with enhanced styling
    totals_start = table_row + 2
    totals = [
        ('Total HT', devis.total_ht),
        ('Remise', devis.total_remise),
        ('Total HT Remise', devis.total_ht_remise),
        ('TVA (18%)', devis.total_tva),
        ('Total TTC', devis.total_ttc),
    ]
    
    # Style the totals section
    tr = totals_start
    for label, value in totals:
        # Label in column F
        label_cell = ws.cell(row=tr, column=6, value=label)
        label_cell.font = bold
        label_cell.alignment = right_align
        if label == 'Total TTC':
            label_cell.fill = PatternFill(start_color=lighter_gray, end_color=lighter_gray, fill_type='solid')
        
        # Value in column G
        val_cell = ws.cell(row=tr, column=7, value=value)
        val_cell.font = bold
        val_cell.number_format = money_format
        if label == 'Total TTC':
            val_cell.fill = PatternFill(start_color=lighter_gray, end_color=lighter_gray, fill_type='solid')
        
        # Add top border for Total TTC
        if label == 'Total TTC':
            label_cell.border = Border(top=Side(border_style='double'))
            val_cell.border = Border(top=Side(border_style='double'))
        
        tr += 1

    # Total en lettres with proper styling
    words_cell = ws.cell(row=tr + 1, column=1, value=f"Total en lettres: {devis.total_ttc_lettres}")
    words_cell.font = bold
    words_cell.alignment = left_align
    ws.merge_cells(start_row=tr + 1, start_column=1, end_row=tr + 1, end_column=5)

    # Response
    filename = f"devis_{devis.numero_devis}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


def liste_materiels(request):
    """Affiche la liste des matériels / produits.

    Cette vue est référencée par `devis_app/urls.py` (path 'materiels/').
    Elle renvoie les catégories (et leurs produits) vers le template `liste_materiels.html`.
    Si le template n'existe pas encore, créer un fichier minimal dans `devis_app/templates/`.
    """
    categories = Categorie.objects.all().prefetch_related('produit_set')
    produits = Produit.objects.all()
    return render(request, 'produits/liste_materiels.html', {
        'categories': categories,
        'produits': produits,
    })


def ajouter_produit(request):
    """Stub view to add a product. Implements minimal POST handling using ProduitForm.

    If you want full behaviour, we can expand this to match your admin UX.
    """
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_materiels')
    else:
        form = ProduitForm()
    return render(request, 'modifier_produit.html', {'form': form})


def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('liste_materiels')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'modifier_produit.html', {'form': form, 'produit': produit})


def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        produit.delete()
        return redirect('liste_materiels')
    return render(request, 'supprimer_produit.html', {'produit': produit})


def ajouter_categorie(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_materiels')
    else:
        form = CategorieForm()
    return render(request, 'modifier_categorie.html', {'form': form})


def export_pdf(request, slug):
    """Export the devis to PDF using WeasyPrint with proper image handling."""
    devis = get_object_or_404(Devis, slug=slug)
    lignes = devis.lignes.all()
    
    # Get the absolute URL for media files
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    base_url = f"{protocol}://{request.get_host()}"
    
    # Prepare context with absolute URLs
    context = {
        'devis': devis,
        'lignes': lignes,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'base_url': base_url,
        'qr_code_url': request.build_absolute_uri(devis.qr_code.url) if devis.qr_code else None,
        'logo_url': request.build_absolute_uri(settings.STATIC_URL + 'images/logo.png')
    }
    
    # Render the template with the full context
    html = render_to_string('devis_template.html', context)
    
    try:
        # Configure WeasyPrint with proper media handling
        base_url = request.build_absolute_uri('/')
        pdf = weasyprint.HTML(
            string=html,
            base_url=base_url,
            url_fetcher=weasyprint.default_url_fetcher
        ).write_pdf(
            stylesheets=[
                weasyprint.CSS(string="""
                    @page { size: A4; margin: 1cm; }
                    body { font-family: Arial, sans-serif; }
                """)
            ]
        )
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="devis_{devis.numero_devis}.pdf"'
        return response
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")  # Debug log
        return HttpResponse(html)  # Fallback to HTML for debugging


def export_devis_word(request, slug):
    """Minimal Word export: creates a simple .docx with basic devis info.

    This is intentionally lightweight to ensure the view exists and works.
    We can expand formatting later to match your desired layout exactly.
    """
    devis = get_object_or_404(Devis, slug=slug)
    lignes = devis.lignes.all()

    doc = Document()
    doc.add_heading(f'Devis N° {devis.numero_devis}', level=1)
    doc.add_paragraph(f'Date: {devis.date_emission.strftime("%d/%m/%Y")}')
    doc.add_paragraph(f'Client: {devis.client.nom} {devis.client.prenom}')
    doc.add_paragraph('')
    doc.add_paragraph('Lignes :')
    for l in lignes:
        doc.add_paragraph(f'- {l.produit.nom} x{l.quantite} : {l.total_ttc}')

    # prepare response
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    filename = f"devis_{devis.numero_devis}_{datetime.now().strftime('%Y%m%d')}.docx"
    response = HttpResponse(bio.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def liste_point_ventes(request):
    # Minimal placeholder: list point_vente names if model exists, otherwise empty list
    try:
        from .models import PointVente
        points = PointVente.objects.all()
    except Exception:
        points = []
    return render(request, 'points_vente/point_vente_list.html', {'points': points})


def ajouter_point_vente(request):
    # placeholder form/view - implement with a ModelForm if needed
    return HttpResponse('Ajout point de vente - à implémenter')


def modifier_point_vente(request, pk):
    return HttpResponse('Modifier point de vente - à implémenter')


def supprimer_point_vente(request, pk):
    return HttpResponse('Supprimer point de vente - à implémenter')



# 🔒 Seulement les superusers ont accès
@login_required(login_url='login')
def admin_dashboard(request):
    from datetime import datetime, timedelta
    from django.db import models
    from django.db.models import Count, Sum, F
    
    # Vérifier que l'utilisateur est un admin
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')

    # Date du jour pour comparaison dernière connexion
    today = timezone.now().date()

    # Statistiques générales
    total_devis = Devis.objects.count()
    total_clients = Client.objects.count()
    total_produits = Produit.objects.count()

    # Statistiques des devis
    current_month = timezone.now().month
    current_year = timezone.now().year
    devis_mois_actuel = Devis.objects.filter(
        date_emission__month=current_month,
        date_emission__year=current_year
    ).count()

    # Top 5 des clients avec le plus de devis
    top_clients = Client.objects.annotate(
        nb_devis=Count('devis')
    ).order_by('-nb_devis')[:5]

    # Top commerciaux avec leurs stats
    top_commerciaux = User.objects.filter(
        profile__role='commercial'
    ).annotate(
        nb_devis=Count('devis'),  # Using the reverse relation from utilisateur field
        total_ca=Sum('devis__total_ttc')
    ).order_by('-nb_devis')[:5]

    # Données pour le graphique des devis par mois
    six_mois = timezone.now() - timedelta(days=180)
    devis_par_mois = (
        Devis.objects
        .filter(date_emission__gte=six_mois)
        .values('date_emission__month', 'date_emission__year')
        .annotate(total=Count('id'))
        .order_by('date_emission__year', 'date_emission__month')
    )

    labels = []
    data = []

    for entry in devis_par_mois:
        month = datetime(
            entry['date_emission__year'],
            entry['date_emission__month'],
            1
        ).strftime('%B %Y')
        labels.append(month)
        data.append(entry['total'])

    # Montant total des devis du mois
    montant_total_mois = Devis.objects.filter(
        date_emission__month=current_month,
        date_emission__year=current_year
    ).aggregate(total=models.Sum('total_ttc'))['total'] or 0

    context = {
        'total_devis': total_devis,
        'total_clients': total_clients,
        'total_produits': total_produits,
        'devis_mois_actuel': devis_mois_actuel,
        'montant_total_mois': montant_total_mois,
        'top_clients': top_clients,
        'top_commerciaux': top_commerciaux,
        'labels': labels,
        'data': data,
        'today': today,
    }
    
    return render(request, 'Dashboard_Admin/admin_dashboard.html', context)


@login_required(login_url='login')
def commerciaux_devis_list(request):
    """
    Affiche la liste des commerciaux (Profile.role == 'commercial')
    avec leur dernier login et la liste des devis qu'ils ont créés.
    Accessible uniquement aux superusers (admin).
    """
    # accès restreint aux admins
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')

    # Récupérer les utilisateurs ayant un profil commercial et précharger leurs devis et actions
    commerciaux = (
        User.objects
        .filter(profile__role='commercial')
        .annotate(nb_devis=Count('devis'))  # Using the reverse relation from utilisateur field
        .prefetch_related('devis', 'actioncommercial_set')
    )

    return render(request, 'commerciaux_devis_list.html', {
        'commerciaux': commerciaux
    })


@login_required(login_url='login')
def create_commercial(request):
    """Permet à l'admin de créer un compte commercial et l'assigner."""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CommercialCreateForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"✅ Commercial {user.username} créé avec succès.")
                return redirect('liste_commerciaux')
            except Exception as e:
                messages.error(request, f"❌ Erreur lors de la création : {str(e)}")
        else:
            messages.error(request, "❌ Le formulaire contient des erreurs. Veuillez vérifier les champs.")
    else:
        form = CommercialCreateForm()

    return render(request, 'create_commercial.html', {'form': form})


@login_required(login_url='login')
def liste_commerciaux(request):
    """Liste tous les commerciaux."""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')
    
    commerciaux = User.objects.filter(profile__role='commercial').select_related('profile', 'profile__point_vente').prefetch_related('devis')
    response = render(request, 'commercial/liste_commerciaux.html', {'commerciaux': commerciaux})
    # Désactiver le cache pour éviter les problèmes d'affichage
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required(login_url='login')
def modifier_commercial(request, user_id):
    """Permet à l'admin de modifier un commercial."""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id, profile__role='commercial')
    
    if request.method == 'POST':
        try:
            # Mise à jour des informations de base
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.is_active = request.POST.get('is_active') == 'on'
            
            # Mise à jour du mot de passe si fourni
            new_password = request.POST.get('new_password', '').strip()
            if new_password:
                user.set_password(new_password)
            
            user.save()
            
            # Mise à jour du profil
            profile = user.profile
            point_vente_id = request.POST.get('point_vente')
            if point_vente_id:
                profile.point_vente_id = int(point_vente_id)
            else:
                profile.point_vente = None
            profile.telephone = request.POST.get('telephone', '')
            profile.save()
            
            messages.success(request, f"✅ Commercial {user.username} modifié avec succès.")
            
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la modification : {str(e)}")
            return redirect('modifier_commercial', user_id=user_id)
        
        # Redirection POST-Redirect-GET pour éviter la re-soumission du formulaire
        return redirect('liste_commerciaux')
    
    points_vente = PointVente.objects.all()
    return render(request, 'commercial/modifier_commercial.html', {
        'commercial': user,
        'points_vente': points_vente
    })


@login_required(login_url='login')
def supprimer_commercial(request, user_id):
    """Permet à l'admin de supprimer un commercial."""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id, profile__role='commercial')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Commercial {username} supprimé avec succès.")
        return redirect('liste_commerciaux?deleted=1')
    
    return render(request, 'commercial/supprimer_commercial.html', {'commercial': user})


@login_required(login_url='login')
def regenerate_qr_codes_view(request):
    """Permet à l'admin de régénérer tous les QR codes."""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')
    
    from .utils import generate_qr_code
    from django.conf import settings
    
    total_devis = Devis.objects.count()
    success_count = 0
    error_count = 0
    started = False
    
    if request.method == 'POST':
        started = True
        devis_list = Devis.objects.all()
        
        for devis in devis_list:
            try:
                qr_image = generate_qr_code(devis.slug)
                if qr_image:
                    devis.qr_code.save(f"qr_{devis.slug}.png", qr_image, save=False)
                    devis.save(update_fields=['qr_code'])
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
        
        messages.success(request, f"✅ {success_count} QR codes régénérés avec succès !")
        if error_count > 0:
            messages.warning(request, f"⚠️ {error_count} erreurs sont survenues.")
    
    return render(request, 'admin/regenerate_qr.html', {
        'total_devis': total_devis,
        'site_url': settings.SITE_URL,
        'started': started,
        'success_count': success_count,
        'error_count': error_count,
    })
    
    return render(request, 'commercial/supprimer_commercial.html', {'commercial': user})