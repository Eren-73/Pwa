from django.shortcuts import render, redirect, get_object_or_404
from .models import Devis, LigneDevis
from .forms import DevisForm, LigneDevisForm
from django.forms import modelformset_factory

def creer_devis(request):
    LigneDevisFormSet = modelformset_factory(LigneDevis, form=LigneDevisForm, extra=3, can_delete=True)

    if request.method == 'POST':
        devis_form = DevisForm(request.POST)
        formset = LigneDevisFormSet(request.POST, queryset=LigneDevis.objects.none())

        if devis_form.is_valid() and formset.is_valid():
            devis = devis_form.save()
            for form in formset:
                ligne = form.save(commit=False)
                ligne.devis = devis
                ligne.save()

            # ✅ Redirection vers la page facture
            return redirect('imprimer_devis', pk=devis.pk) 
        else:
            # ← AJOUT DES PRINTS POUR DEBUG
            print("Devis form errors:", devis_form.errors)
            print("Formset errors:", formset.errors)

    else:
        devis_form = DevisForm()
        formset = LigneDevisFormSet(queryset=LigneDevis.objects.none())

    return render(request, 'creer_devis.html', {
        'devis_form': devis_form,
        'formset': formset
    })


def imprimer_devis(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    lignes = devis.lignes.all()  # si tu as une relation reverse "lignes"
    
    # ✅ Nom exact du template avec .html
    return render(request, 'devis_template.html', {
        'devis': devis,
        'lignes': lignes
    })