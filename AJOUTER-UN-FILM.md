# Ajouter un film sur le site

Cinq minutes, aucun logiciel à installer. Les films sont hébergés sur YouTube (en mode
« non répertoriée », donc invisibles hors du site) et le site lit la liste dans un seul
fichier : `assets/films.json`.

## 1. Mettre le film sur YouTube

1. Connectez-vous à YouTube avec le compte de l'association (`asso.slave@gmail.com`).
2. Cliquez sur **Créer → Importer une vidéo**, choisissez le fichier.
3. Titre : le nom du film. Visibilité : **Non répertoriée**.
4. Une fois l'import terminé, copiez le lien. L'identifiant est ce qui suit `v=` :
   dans `https://www.youtube.com/watch?v=Nv8xsx0MZLw`, l'identifiant est `Nv8xsx0MZLw`
   (11 caractères).

## 2. Ajouter une ligne dans la liste

1. Ouvrez https://github.com/regenfren/slave-website/edit/main/assets/films.json
   (il faut un compte GitHub ajouté au projet ; demandez à Tim si le lien refuse).
2. Descendez tout en bas. Le dernier film se termine par `}`. Ajoutez une virgule juste
   après ce `}`, puis collez le bloc ci-dessous en remplissant les champs.
3. Cliquez sur **Commit changes** (deux fois, le bouton vert). Le site se met à jour tout
   seul en une ou deux minutes.

```json
    {
      "id": "nom-du-film",
      "title": "Nom du film",
      "tagline": { "en": "", "fr": "" },
      "school": "kedge",
      "term": "2026-fall",
      "course": { "en": "Nom du cours", "fr": "Nom du cours" },
      "team": "Nom de l'équipe",
      "language": "fr",
      "duration": 300,
      "youtube": "IDENTIFIANT_YOUTUBE",
      "poster": "",
      "file": "",
      "synopsis": { "en": "", "fr": "" }
    }
```

Ce que veut dire chaque champ :

| Champ | À mettre |
|---|---|
| `id` | un mot unique, en minuscules, sans espaces ni accents (`nova-night`) |
| `title` | le titre affiché |
| `tagline` | une phrase d'accroche, facultatif |
| `school` | `kedge`, `cnam`, `iae`, `ubm` ou `cafa` (liste en haut du fichier, section `schools`) |
| `term` | `2025-fall`, `2026-spring`, `2026-fall`… (section `terms` ; ajoutez-y la ligne si le semestre n'existe pas encore) |
| `course` | le nom du cours, en anglais et en français |
| `team` | l'équipe ou les prénoms des auteurs |
| `language` | `fr` ou `en` (langue du film) |
| `duration` | durée en secondes, facultatif (5 min = `300`) |
| `youtube` | **l'identifiant copié à l'étape 1. C'est le seul champ obligatoire : sans lui le film n'apparaît pas.** |
| `poster` | laissez vide, la vignette YouTube est utilisée automatiquement |
| `file` | laissez vide (nom du fichier d'origine, pour les archives) |
| `synopsis` | le résumé du film, facultatif, dans les deux langues |

Le film apparaît sur https://regenfren.github.io/slave-website/films.html, dans le bloc
de son école et de son semestre. Il apparaît aussi sur la version française sans rien faire
de plus.

## Si ça ne marche pas

- La page affiche « La liste des films n'a pas pu être chargée » : il manque une virgule
  ou un guillemet dans le fichier. Vérifiez le bloc que vous venez de coller, ou envoyez le
  lien à Tim.
- Le film n'apparaît pas : le champ `youtube` est vide ou l'identifiant est faux. Ouvrez
  `https://www.youtube.com/watch?v=IDENTIFIANT` pour vérifier.
- Pour retirer un film : effacez son bloc (et la virgule qui le précède).

## Pour une nouvelle école

En haut du fichier, section `schools`, ajoutez une ligne sur le modèle des autres :

```json
    "iae": { "name": "IAE Bordeaux", "city": "Bordeaux" },
```

L'ordre des écoles dans cette section est l'ordre d'affichage sur la page.
