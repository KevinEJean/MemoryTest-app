# Description du Jeux :
Le jeu commence par l'apparition d'un ou plusieurs points clignotants a des position aleatoire (le nombre correspond au niveau), que le joueur doit retrouver en les dirigeant depuis le centre de la matrice vers leur emplacement précédent. L'interface utilisateur comprend des boutons pour démarrer, réinitialiser et terminer la partie. Aussi, il affiche l'état du jeu, le score, et un paramètre de difficulté. Un bouton physique permet d'afficher un dessin enregistré, puis un autre enregistre un dessin a la fois. Si, j'ai le temps, un second mode de jeu, inspiré du "memory leap frog", est également prévu.

# Materiel utilise :
Le projet inclut un buzzer pour signaler un échec ou un tentative reussie, une LED RGB pour indiquer l'état (échec(rouge), réussite(vert), en jeux(bleue), connexion(jaune), connecte(blanc)), un joystick pour déplacer un point, un bouton poussoir pour basculer entre les modes sauvegarder/afficher des dessins, ainsi qu'une matrice LED 8x8 pour le jeu principal.

# À faire :
Configurer le WiFi, développer un interface utilisateur, mettre en place un service de communication et automatiser le lancement des scripts (WiFi, backend, frontend).

# Solution :
Pour ce faire, le wifi sera configurer sur le serveur 'rasp08' a l'aide de 'NetwerkManager' et 'dnsmasq.d'. Ensuite, l'interface sera un developper avec les language de programmation suivant : HTML, CSS et Javascript.
Puis, le service de communication utiliser sera HTTP REST, parce qu'il facilitera l'echange de donnee entre les differents components. Finalement, le lancement des scripts sera effectuer en tent que service 'systemd' de type 'oneshot'.