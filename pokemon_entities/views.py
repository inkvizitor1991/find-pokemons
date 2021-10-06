import folium

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from .models import Pokemon, PokemonEntity

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemon_entities = PokemonEntity.objects.all()
    for pokemon_entity in pokemon_entities:
        photo = request.build_absolute_uri(
            pokemon_entity.pokemon.photo.url
        )
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            photo
        )
    pokemons = Pokemon.objects.all()
    pokemons_on_page = []
    for pokemon in pokemons:
        photo = request.build_absolute_uri(pokemon.photo.url)
        pokemons_on_page.append({
            'img_url': photo,
            'pokemon_id': pokemon.id,
            'title_ru': pokemon.title,
        })
    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemon_entities = PokemonEntity.objects.all()
    for pokemon_entity in pokemon_entities:
        photo = request.build_absolute_uri(
            pokemon_entity.pokemon.photo.url
        )
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            photo
        )
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        raise Http404('Покемон не найден.')

    photo = request.build_absolute_uri(pokemon.photo.url)
    if pokemon.previous_evolution:
        previous_evolution = {
            'title_ru': pokemon.previous_evolution.title,
            'pokemon_id': pokemon.previous_evolution.id,
            'img_url': request.build_absolute_uri(
                pokemon.previous_evolution.photo.url
            )
        }
    else:
        previous_evolution = None

    next_evolution = {}
    if pokemon.next_evolutions:
        evolving_pokemons = pokemon.next_evolutions.all()
        for evolving_pokemon in evolving_pokemons:
            next_evolution.update({
                'title_ru': evolving_pokemon.title,
                'pokemon_id': evolving_pokemon.id,
                'img_url': request.build_absolute_uri(
                    evolving_pokemon.photo.url)
            })
    else:
        next_evolution = None

    pokemons_on_page = {
        'img_url': photo,
        'pokemon_id': pokemon.id,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'previous_evolution': previous_evolution,
        'next_evolution': next_evolution,

    }
    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemons_on_page
    })
