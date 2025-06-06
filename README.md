<!-- vim: set spelllang=fr: -->

# Calculum — Club d’algorithmique compétitive universitaire de l’Université de Montréal

[Voir le site web](https://calculum.ca)

# Comment éxécuter le site en local / publier le serveur

Installez racket et pollen:

sudo apt install racket

raco pkg install pollen gregor

raco pkg-env .penv

Dans le .penv environement, le makefile s'attend a un activate.sh script.

Je ne sais pas c'est quoi ce script, j'ai donc simplement cree un script vide et manuellement add les dependencies.

Apres ->

make pollen

make local

make serve
