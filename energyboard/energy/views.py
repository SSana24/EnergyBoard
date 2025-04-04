import pandas as pd
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Sum
from datetime import datetime
from .models import EnergyData
from .forms import UploadCSVForm


def upload_csv(request):
    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            try:
                # Lire le fichier CSV avec le bon séparateur et encodage
                data = pd.read_csv(csv_file, sep=';', decimal=',', encoding='utf-8')

                # Vérifier les noms des colonnes
                print("Colonnes détectées :", data.columns)
                data.columns = data.columns.str.strip()  # Supprime les espaces autour des noms de colonnes
                print("Colonnes après nettoyage :", data.columns)

                # Insérer les données en base
                for _, row in data.iterrows():
                     # Convertir la date en format YYYY-MM-DD
                    date_str = str(row['Date']).strip()  # S'assurer que c'est une chaîne
                    date_obj = datetime.strptime(date_str, "%Y")  # Convertir l'année en date
                    if not EnergyData.objects.filter(date=row['Date'], region=row['Region']).exists():
                        EnergyData.objects.create(
                            date=date_obj,
                            region=row['Region'],
                            consumption_twh=row['Valeur (TWh)']
                        )                
                # Redirection après avoir ajouté toutes les données
                return redirect("data_list")

            except Exception as e:
                print(f"Erreur lors du traitement du fichier : {e}")
                return render(request, "energy/upload.html", {"form": form, "error": "Erreur d'importation. Vérifiez le format du fichier."})

    else:
        form = UploadCSVForm()

    return render(request, "energy/upload.html", {"form": form})    
# Afficher les données
def data_list(request):
    # Récupérer les paramètres de filtrage depuis l'URL
    selected_year = request.GET.get("year", "")
    selected_region = request.GET.get("region", "")

    # Filtrer les données selon les choix de l'utilisateur
    data_list = EnergyData.objects.all()

    if selected_year:
        data_list = data_list.filter(date__year=selected_year)

    if selected_region:
        data_list = data_list.filter(region=selected_region)
    # Évite les doublons en affichage
    data_list = data_list.distinct()

    #  Ajouter la pagination (10 éléments par page)
    paginator = Paginator(data_list, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    #  Données pour les graphiques
    consumption_by_region = (
        data_list.values("region")
        .annotate(total_consumption=Sum("consumption_twh"))
        .order_by("-total_consumption")
    )

    consumption_by_year = (
        EnergyData.objects.values("date__year")
        .annotate(total_consumption=Sum("consumption_twh"))
        .order_by("date__year")
    )

    return render(request, "energy/data_list.html", {
        "page_obj": page_obj,
        "selected_year": selected_year,
        "selected_region": selected_region,
        "consumption_by_region": list(consumption_by_region),
        "consumption_by_year": list(consumption_by_year),
    })
