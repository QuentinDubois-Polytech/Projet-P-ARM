README
=======

# Introduction

Le projet consiste à terminer l'implémentation d'un processeur simplifié sous l'architecture ARM Cortex-M0. Nous utilisons pour le codage des instructions le codage Thumb. Pour réaliser cette tâche nous utilisons le simulateur Logisim.

Les contributeurs de ce projet sont [Quentin Dubois](https://github.com/QuentinDubois-Polytech), [Ludovic Bailet](https://github.com/Ludovic-BAILET), [Bastian Bezes](https://github.com/Authen15) et [Aurélia Chabanier](https://github.com/AureliaChabanier), tous membres de l'équipe P-ARMESA-N. Nous sommes tous élèves de l'école d'ingénieur Polytech Nice-Sophia de la filière Sciences Informatiques.

### Lien Github

Vous pouvez trouver le projet en cliquant sur ce [lien](https://github.com/QuentinDubois-Polytech/Projet-P-ARM).

# Fonctionnement de l'assembleur

### Prérequis
* Python 3.10 (ou supérieur)

### Execution du programme

#### Commande:
`py ./assembleur.py ./nom_fichier.s`

L'exécution de cette commande affiche les instructions en binaire sur le terminal. Elle génère aussi un fichier du même nom en .bin, soit nom_fichier.bin à l'emplacement de l'exécution de la commande.